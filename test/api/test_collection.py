import re
from datetime import datetime, timedelta, timezone
from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Collection, CollectionFlag, CollectionFlagAudit, Scope
from odp.lib.formats import DOI_REGEX
from test.api import assert_empty_result, assert_forbidden, all_scopes, all_scopes_excluding, assert_unprocessable
from test.factories import CollectionFactory, ProjectFactory, ProviderFactory, FlagFactory, SchemaFactory


@pytest.fixture
def collection_batch():
    """Create and commit a batch of Collection instances."""
    collections = [CollectionFactory() for _ in range(randint(3, 5))]
    ProjectFactory.create_batch(randint(0, 3), collections=collections)
    return collections


@pytest.fixture
def collection_batch_no_projects():
    """Create and commit a batch of Collection instances
    without projects, for testing the update API - we cannot
    assign projects to collections, only the other way around."""
    return [CollectionFactory() for _ in range(randint(3, 5))]


def collection_build(provider=None, **id):
    """Build and return an uncommitted Collection instance.
    Referenced provider is however committed."""
    return CollectionFactory.build(
        **id,
        provider=provider or (provider := ProviderFactory()),
        provider_id=provider.id,
    )


def project_ids(collection):
    return tuple(project.id for project in collection.projects)


def assert_db_state(collections):
    """Verify that the DB collection table contains the given collection batch."""
    Session.expire_all()
    result = Session.execute(select(Collection)).scalars().all()
    assert set((row.id, row.name, row.doi_key, row.provider_id, project_ids(row)) for row in result) \
           == set((collection.id, collection.name, collection.doi_key, collection.provider_id, project_ids(collection)) for collection in collections)


def assert_db_flag_state(collection_id, collection_flag):
    """Verify that the collection_flag table contains the given collection flag."""
    Session.expire_all()
    result = Session.execute(select(CollectionFlag)).scalar_one_or_none()
    if collection_flag:
        assert result.collection_id == collection_id
        assert result.flag_id == collection_flag['flag_id']
        assert result.user_id is None
        assert result.data == collection_flag['data']
        assert datetime.now(timezone.utc) - timedelta(seconds=120) < result.timestamp < datetime.now(timezone.utc)
    else:
        assert result is None


def assert_flag_audit_log(*entries):
    result = Session.execute(select(CollectionFlagAudit)).scalars().all()
    assert len(result) == len(entries)
    for n, row in enumerate(result):
        assert row.client_id == 'odp.test'
        assert row.user_id is None
        assert row.command == entries[n]['command']
        assert datetime.now(timezone.utc) - timedelta(seconds=120) < row.timestamp < datetime.now(timezone.utc)
        assert row._collection_id == entries[n]['collection_id']
        assert row._flag_id == entries[n]['collection_flag']['flag_id']
        assert row._user_id is None
        if row.command in ('insert', 'update'):
            assert row._data == entries[n]['collection_flag']['data']
        elif row.command == 'delete':
            assert row._data is None
        else:
            assert False


def assert_json_collection_result(response, json, collection):
    """Verify that the API result matches the given collection object."""
    assert response.status_code == 200
    assert json['id'] == collection.id
    assert json['name'] == collection.name
    assert json['doi_key'] == collection.doi_key
    assert json['provider_id'] == collection.provider_id
    assert tuple(json['project_ids']) == project_ids(collection)


def assert_json_collection_results(response, json, collections):
    """Verify that the API result list matches the given collection batch."""
    items = json['items']
    assert json['total'] == len(items) == len(collections)
    items.sort(key=lambda i: i['id'])
    collections.sort(key=lambda c: c.id)
    for n, collection in enumerate(collections):
        assert_json_collection_result(response, items[n], collection)


def assert_json_flag_result(response, json, collection_flag):
    """Verify that the API result matches the given collection flag dict."""
    assert response.status_code == 200
    assert json['flag_id'] == collection_flag['flag_id']
    assert json['user_id'] is None
    assert json['user_name'] is None
    assert json['data'] == collection_flag['data']
    assert datetime.now(timezone.utc) - timedelta(seconds=120) < datetime.fromisoformat(json['timestamp']) < datetime.now(timezone.utc)


def assert_doi_result(response, collection):
    assert response.status_code == 200
    assert re.match(DOI_REGEX, doi := response.json()) is not None
    prefix, _, suffix = doi.rpartition('.')
    assert prefix == f'10.15493/{collection.doi_key}'
    assert re.match(r'^\d{8}$', suffix) is not None


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.COLLECTION_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.COLLECTION_READ), False),
])
def test_list_collections(api, collection_batch, scopes, authorized):
    r = api(scopes).get('/collection/')
    if authorized:
        assert_json_collection_results(r, r.json(), collection_batch)
    else:
        assert_forbidden(r)
    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.COLLECTION_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.COLLECTION_READ), False),
])
def test_list_collections_with_provider_specific_api_client(api, collection_batch, scopes, authorized):
    api_client_provider = collection_batch[2].provider
    r = api(scopes, api_client_provider).get('/collection/')
    if authorized:
        assert_json_collection_results(r, r.json(), [collection_batch[2]])
    else:
        assert_forbidden(r)
    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.COLLECTION_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.COLLECTION_READ), False),
])
def test_get_collection(api, collection_batch, scopes, authorized):
    r = api(scopes).get(f'/collection/{collection_batch[2].id}')
    if authorized:
        assert_json_collection_result(r, r.json(), collection_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.COLLECTION_READ], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.COLLECTION_READ), True, False),
])
def test_get_collection_with_provider_specific_api_client(api, collection_batch, scopes, matching_provider, authorized):
    api_client_provider = collection_batch[2].provider if matching_provider else collection_batch[1].provider
    r = api(scopes, api_client_provider).get(f'/collection/{collection_batch[2].id}')
    if authorized:
        assert_json_collection_result(r, r.json(), collection_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.COLLECTION_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.COLLECTION_ADMIN), False),
])
def test_create_collection(api, collection_batch, scopes, authorized):
    modified_collection_batch = collection_batch + [collection := collection_build()]
    r = api(scopes).post('/collection/', json=dict(
        id=collection.id,
        name=collection.name,
        doi_key=collection.doi_key,
        provider_id=collection.provider_id,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_collection_batch)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.COLLECTION_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.COLLECTION_ADMIN), True, False),
])
def test_create_collection_with_provider_specific_api_client(api, collection_batch, scopes, matching_provider, authorized):
    api_client_provider = collection_batch[2].provider if matching_provider else collection_batch[1].provider
    modified_collection_batch = collection_batch + [collection := collection_build(
        provider=collection_batch[2].provider
    )]
    r = api(scopes, api_client_provider).post('/collection/', json=dict(
        id=collection.id,
        name=collection.name,
        doi_key=collection.doi_key,
        provider_id=collection.provider_id,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_collection_batch)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.COLLECTION_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.COLLECTION_ADMIN), False),
])
def test_update_collection(api, collection_batch_no_projects, scopes, authorized):
    modified_collection_batch = collection_batch_no_projects.copy()
    modified_collection_batch[2] = (collection := collection_build(
        id=collection_batch_no_projects[2].id,
    ))
    r = api(scopes).put('/collection/', json=dict(
        id=collection.id,
        name=collection.name,
        doi_key=collection.doi_key,
        provider_id=collection.provider_id,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_collection_batch)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch_no_projects)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.COLLECTION_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.COLLECTION_ADMIN), True, False),
])
def test_update_collection_with_provider_specific_api_client(api, collection_batch_no_projects, scopes, matching_provider, authorized):
    api_client_provider = collection_batch_no_projects[2].provider if matching_provider else collection_batch_no_projects[1].provider
    modified_collection_batch = collection_batch_no_projects.copy()
    modified_collection_batch[2] = (collection := collection_build(
        id=collection_batch_no_projects[2].id,
        provider=collection_batch_no_projects[2].provider,
    ))
    r = api(scopes, api_client_provider).put('/collection/', json=dict(
        id=collection.id,
        name=collection.name,
        doi_key=collection.doi_key,
        provider_id=collection.provider_id,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_collection_batch)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch_no_projects)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.COLLECTION_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.COLLECTION_ADMIN), False),
])
def test_delete_collection(api, collection_batch, scopes, authorized):
    modified_collection_batch = collection_batch.copy()
    del modified_collection_batch[2]
    r = api(scopes).delete(f'/collection/{collection_batch[2].id}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_collection_batch)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.COLLECTION_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.COLLECTION_ADMIN), True, False),
])
def test_delete_collection_with_provider_specific_api_client(api, collection_batch, scopes, matching_provider, authorized):
    api_client_provider = collection_batch[2].provider if matching_provider else collection_batch[1].provider
    modified_collection_batch = collection_batch.copy()
    del modified_collection_batch[2]
    r = api(scopes, api_client_provider).delete(f'/collection/{collection_batch[2].id}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_collection_batch)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.COLLECTION_FLAG_PUBLISH], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.COLLECTION_FLAG_PUBLISH), False),
])
def test_flag_collection(api, collection_batch, scopes, authorized):
    client = api(scopes)
    FlagFactory(
        id='collection-publish',
        scope=Session.get(Scope, ODPScope.COLLECTION_FLAG_PUBLISH) or Scope(id=ODPScope.COLLECTION_FLAG_PUBLISH),
        schema=SchemaFactory(
            type='flag',
            uri='https://odp.saeon.ac.za/schema/flag/generic',
        ),
    )

    # insert flag
    r = client.post(
        f'/collection/{(collection_id := collection_batch[2].id)}/flag',
        json=(collection_flag_v1 := dict(
            flag_id='collection-publish',
            data={
                'comment': 'Hello World',
            },
        )))
    if authorized:
        assert_json_flag_result(r, r.json(), collection_flag_v1)
        assert_db_flag_state(collection_id, collection_flag_v1)
        assert_flag_audit_log(
            dict(command='insert', collection_id=collection_id, collection_flag=collection_flag_v1),
        )
    else:
        assert_forbidden(r)
        assert_db_flag_state(collection_id, None)
        assert_flag_audit_log()
    assert_db_state(collection_batch)

    # update flag
    r = client.post(
        f'/collection/{collection_id}/flag',
        json=(collection_flag_v2 := dict(
            flag_id='collection-publish',
            data={},
        )))
    if authorized:
        assert_json_flag_result(r, r.json(), collection_flag_v2)
        assert_db_flag_state(collection_id, collection_flag_v2)
        assert_flag_audit_log(
            dict(command='insert', collection_id=collection_id, collection_flag=collection_flag_v1),
            dict(command='update', collection_id=collection_id, collection_flag=collection_flag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_flag_state(collection_id, None)
        assert_flag_audit_log()
    assert_db_state(collection_batch)

    # delete flag
    r = client.delete(f'/collection/{collection_id}/flag/{collection_flag_v1["flag_id"]}')
    if authorized:
        assert_empty_result(r)
        assert_db_flag_state(collection_id, None)
        assert_flag_audit_log(
            dict(command='insert', collection_id=collection_id, collection_flag=collection_flag_v1),
            dict(command='update', collection_id=collection_id, collection_flag=collection_flag_v2),
            dict(command='delete', collection_id=collection_id, collection_flag=collection_flag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_flag_state(collection_id, None)
        assert_flag_audit_log()
    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.COLLECTION_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.COLLECTION_READ), False),
])
def test_get_new_doi(api, collection_batch, scopes, authorized):
    r = api(scopes).get(f'/collection/{(collection := collection_batch[2]).id}/doi/new')
    if authorized:
        if collection.doi_key:
            assert_doi_result(r, collection)
        else:
            assert_unprocessable(r, 'The collection does not have a DOI key')
    else:
        assert_forbidden(r)
    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.COLLECTION_READ], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.COLLECTION_READ), True, False),
])
def test_get_new_doi_with_provider_specific_api_client(api, collection_batch, scopes, matching_provider, authorized):
    api_client_provider = collection_batch[2].provider if matching_provider else collection_batch[1].provider
    r = api(scopes, api_client_provider).get(f'/collection/{(collection := collection_batch[2]).id}/doi/new')
    if authorized:
        if collection.doi_key:
            assert_doi_result(r, collection)
        else:
            assert_unprocessable(r, 'The collection does not have a DOI key')
    else:
        assert_forbidden(r)
    assert_db_state(collection_batch)
