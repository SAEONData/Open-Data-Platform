import re
from datetime import datetime
from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Collection, CollectionTag, CollectionTagAudit, Scope, ScopeType
from odp.lib.formats import DOI_REGEX
from test.api import (CollectionAuth, all_scopes, all_scopes_excluding, assert_conflict, assert_empty_result, assert_forbidden, assert_new_timestamp,
                      assert_not_found, assert_unprocessable)
from test.factories import (ClientFactory, CollectionFactory, CollectionTagFactory, ProjectFactory, ProviderFactory, RoleFactory, SchemaFactory,
                            TagFactory)


@pytest.fixture
def collection_batch():
    """Create and commit a batch of Collection instances,
    with associated projects, clients and roles."""
    collections = [CollectionFactory() for _ in range(randint(3, 5))]
    ProjectFactory.create_batch(randint(0, 3), collections=collections)
    for collection in collections:
        ClientFactory.create_batch(randint(0, 3), collection=collection)
        RoleFactory.create_batch(randint(0, 3), collection=collection)
    return collections


@pytest.fixture
def collection_batch_no_projects():
    """Create and commit a batch of Collection instances
    without projects, for testing the update API - we cannot
    assign projects to collections, only the other way around."""
    collections = [CollectionFactory() for _ in range(randint(3, 5))]
    for collection in collections:
        ClientFactory.create_batch(randint(0, 3), collection=collection)
        RoleFactory.create_batch(randint(0, 3), collection=collection)
    return collections


def collection_build(**id):
    """Build and return an uncommitted Collection instance.
    Referenced provider is however committed."""
    return CollectionFactory.build(
        **id,
        provider=(provider := ProviderFactory()),
        provider_id=provider.id,
    )


def project_ids(collection):
    return tuple(project.id for project in collection.projects)


def client_ids(collection):
    return tuple(client.id for client in collection.clients if client.id != 'odp.test')


def role_ids(collection):
    return tuple(role.id for role in collection.roles)


def assert_db_state(collections):
    """Verify that the DB collection table contains the given collection batch."""
    Session.expire_all()
    result = Session.execute(select(Collection)).scalars().all()
    assert set((row.id, row.name, row.doi_key, row.provider_id, project_ids(row), client_ids(row), role_ids(row)) for row in result) \
           == set((collection.id, collection.name, collection.doi_key, collection.provider_id, project_ids(collection), client_ids(collection),
                   role_ids(collection)) for collection in collections)


def assert_db_tag_state(collection_id, *collection_tags):
    """Verify that the collection_tag table contains the given collection tags."""
    Session.expire_all()
    result = Session.execute(select(CollectionTag)).scalars().all()
    assert len(result) == len(collection_tags)
    for n, row in enumerate(result):
        assert row.collection_id == collection_id
        assert_new_timestamp(row.timestamp)
        try:
            # collection_tags[n] is a dict we posted to the collection API
            assert row.tag_id == collection_tags[n]['tag_id']
            assert row.user_id is None
            assert row.data == collection_tags[n]['data']
        except TypeError:
            # collection_tags[n] is an object we created with CollectionTagFactory
            assert row.tag_id == collection_tags[n].tag_id
            assert row.user_id == collection_tags[n].user_id
            assert row.data == collection_tags[n].data


def assert_tag_audit_log(*entries):
    result = Session.execute(select(CollectionTagAudit)).scalars().all()
    assert len(result) == len(entries)
    for n, row in enumerate(result):
        assert row.client_id == 'odp.test'
        assert row.user_id is None
        assert row.command == entries[n]['command']
        assert_new_timestamp(row.timestamp)
        assert row._collection_id == entries[n]['collection_id']
        assert row._tag_id == entries[n]['collection_tag']['tag_id']
        assert row._user_id is None
        if row.command in ('insert', 'update'):
            assert row._data == entries[n]['collection_tag']['data']
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
    assert tuple(j for j in json['client_ids'] if j != 'odp.test') == client_ids(collection)
    assert tuple(json['role_ids']) == role_ids(collection)


def assert_json_collection_results(response, json, collections):
    """Verify that the API result list matches the given collection batch."""
    items = json['items']
    assert json['total'] == len(items) == len(collections)
    items.sort(key=lambda i: i['id'])
    collections.sort(key=lambda c: c.id)
    for n, collection in enumerate(collections):
        assert_json_collection_result(response, items[n], collection)


def assert_json_tag_result(response, json, collection_tag):
    """Verify that the API result matches the given collection tag dict."""
    assert response.status_code == 200
    assert json['tag_id'] == collection_tag['tag_id']
    assert json['user_id'] is None
    assert json['user_name'] is None
    assert json['data'] == collection_tag['data']
    assert_new_timestamp(datetime.fromisoformat(json['timestamp']))
    assert json['flag'] == collection_tag['flag']
    assert json['public'] == collection_tag['public']


def assert_doi_result(response, collection):
    assert response.status_code == 200
    assert re.match(DOI_REGEX, doi := response.json()) is not None
    prefix, _, suffix = doi.rpartition('.')
    assert prefix == f'10.15493/{collection.doi_key}'
    assert re.match(r'^\d{8}$', suffix) is not None


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_READ),
])
def test_list_collections(api, collection_batch, scopes, collection_auth):
    authorized = ODPScope.COLLECTION_READ in scopes

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
        expected_result_batch = [collection_batch[2]]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = CollectionFactory()
        expected_result_batch = [api_client_collection]
        collection_batch += [api_client_collection]
    else:
        api_client_collection = None
        expected_result_batch = collection_batch

    r = api(scopes, api_client_collection).get('/collection/')

    if authorized:
        assert_json_collection_results(r, r.json(), expected_result_batch)
    else:
        assert_forbidden(r)

    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_READ),
])
def test_get_collection(api, collection_batch, scopes, collection_auth):
    authorized = ODPScope.COLLECTION_READ in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    r = api(scopes, api_client_collection).get(f'/collection/{collection_batch[2].id}')

    if authorized:
        assert_json_collection_result(r, r.json(), collection_batch[2])
    else:
        assert_forbidden(r)

    assert_db_state(collection_batch)


def test_get_collection_not_found(api, collection_batch, collection_auth):
    scopes = [ODPScope.COLLECTION_READ]
    authorized = collection_auth == CollectionAuth.NONE

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = collection_batch[2]

    r = api(scopes, api_client_collection).get('/collection/foo')

    if authorized:
        assert_not_found(r)
    else:
        assert_forbidden(r)

    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_ADMIN),
])
def test_create_collection(api, collection_batch, scopes, collection_auth):
    # note that collection-specific auth will never allow creating a new collection
    authorized = ODPScope.COLLECTION_ADMIN in scopes and \
                 collection_auth == CollectionAuth.NONE

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = collection_batch[2]

    modified_collection_batch = collection_batch + [collection := collection_build()]

    r = api(scopes, api_client_collection).post('/collection/', json=dict(
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


def test_create_collection_conflict(api, collection_batch, collection_auth):
    scopes = [ODPScope.COLLECTION_ADMIN]
    authorized = collection_auth == CollectionAuth.NONE

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = collection_batch[2]

    collection = collection_build(id=collection_batch[2].id)

    r = api(scopes, api_client_collection).post('/collection/', json=dict(
        id=collection.id,
        name=collection.name,
        doi_key=collection.doi_key,
        provider_id=collection.provider_id,
    ))

    if authorized:
        assert_conflict(r, 'Collection id is already in use')
    else:
        assert_forbidden(r)

    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_ADMIN),
])
def test_update_collection(api, collection_batch_no_projects, scopes, collection_auth):
    authorized = ODPScope.COLLECTION_ADMIN in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch_no_projects[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch_no_projects[1]
    else:
        api_client_collection = None

    modified_collection_batch = collection_batch_no_projects.copy()
    modified_collection_batch[2] = (collection := collection_build(
        id=collection_batch_no_projects[2].id,
        clients=collection_batch_no_projects[2].clients,
        roles=collection_batch_no_projects[2].roles,
    ))

    r = api(scopes, api_client_collection).put('/collection/', json=dict(
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


def test_update_collection_not_found(api, collection_batch_no_projects, collection_auth):
    scopes = [ODPScope.COLLECTION_ADMIN]
    authorized = collection_auth == CollectionAuth.NONE

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = collection_batch_no_projects[2]

    collection = collection_build(id='foo')

    r = api(scopes, api_client_collection).put('/collection/', json=dict(
        id=collection.id,
        name=collection.name,
        doi_key=collection.doi_key,
        provider_id=collection.provider_id,
    ))

    if authorized:
        assert_not_found(r)
    else:
        assert_forbidden(r)

    assert_db_state(collection_batch_no_projects)


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_ADMIN),
])
def test_delete_collection(api, collection_batch, scopes, collection_auth):
    authorized = ODPScope.COLLECTION_ADMIN in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    modified_collection_batch = collection_batch.copy()
    del modified_collection_batch[2]

    r = api(scopes, api_client_collection).delete(f'/collection/{collection_batch[2].id}')

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_collection_batch)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch)


def test_delete_collection_not_found(api, collection_batch, collection_auth):
    scopes = [ODPScope.COLLECTION_ADMIN]
    authorized = collection_auth == CollectionAuth.NONE

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = collection_batch[2]

    r = api(scopes, api_client_collection).delete('/collection/foo')

    if authorized:
        assert_not_found(r)
    else:
        assert_forbidden(r)

    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_PUBLISH],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_PUBLISH),
])
def test_tag_collection(api, collection_batch, scopes, collection_auth):
    authorized = ODPScope.COLLECTION_PUBLISH in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    client = api(scopes, api_client_collection)
    tag = TagFactory(
        id='Collection.Publish',
        type='collection',
        scope=Session.get(
            Scope, (ODPScope.COLLECTION_PUBLISH, ScopeType.odp)
        ) or Scope(
            id=ODPScope.COLLECTION_PUBLISH, type=ScopeType.odp
        ),
        schema=SchemaFactory(
            type='tag',
            uri='https://odp.saeon.ac.za/schema/tag/generic',
        ),
    )

    # insert tag
    r = client.post(
        f'/collection/{(collection_id := collection_batch[2].id)}/tag',
        json=(collection_tag_v1 := dict(
            tag_id='Collection.Publish',
            data={
                'comment': 'Hello World',
            },
        )))
    if authorized:
        assert_json_tag_result(r, r.json(), collection_tag_v1 | dict(flag=tag.flag, public=tag.public))
        assert_db_tag_state(collection_id, collection_tag_v1)
        assert_tag_audit_log(
            dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_v1),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(collection_id)
        assert_tag_audit_log()
    assert_db_state(collection_batch)

    # update tag
    r = client.post(
        f'/collection/{collection_id}/tag',
        json=(collection_tag_v2 := dict(
            tag_id='Collection.Publish',
            data={},
        )))
    if authorized:
        assert_json_tag_result(r, r.json(), collection_tag_v2 | dict(flag=tag.flag, public=tag.public))
        assert_db_tag_state(collection_id, collection_tag_v2)
        assert_tag_audit_log(
            dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_v1),
            dict(command='update', collection_id=collection_id, collection_tag=collection_tag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(collection_id)
        assert_tag_audit_log()
    assert_db_state(collection_batch)

    # delete tag
    r = client.delete(f'/collection/{collection_id}/tag/{collection_tag_v1["tag_id"]}')
    if authorized:
        assert_empty_result(r)
        assert_db_tag_state(collection_id)
        assert_tag_audit_log(
            dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_v1),
            dict(command='update', collection_id=collection_id, collection_tag=collection_tag_v2),
            dict(command='delete', collection_id=collection_id, collection_tag=collection_tag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(collection_id)
        assert_tag_audit_log()
    assert_db_state(collection_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_READ),
])
def test_get_new_doi(api, collection_batch, scopes, collection_auth):
    authorized = ODPScope.COLLECTION_READ in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    r = api(scopes, api_client_collection).get(f'/collection/{(collection := collection_batch[2]).id}/doi/new')

    if authorized:
        if collection.doi_key:
            assert_doi_result(r, collection)
        else:
            assert_unprocessable(r, 'The collection does not have a DOI key')
    else:
        assert_forbidden(r)

    assert_db_state(collection_batch)


@pytest.fixture(params=[True, False])
def flag(request):
    return request.param


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_PUBLISH],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_PUBLISH),
])
def test_tag_collection_multi(api, collection_batch, scopes, collection_auth, flag):
    authorized = ODPScope.COLLECTION_PUBLISH in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    client = api(scopes, api_client_collection)

    collection_tag_1 = CollectionTagFactory(
        collection=collection_batch[2],
        tag=(tag := TagFactory(
            id='Collection.Publish',
            type='collection',
            flag=flag,
            scope=Session.get(
                Scope, (ODPScope.COLLECTION_PUBLISH, ScopeType.odp)
            ) or Scope(
                id=ODPScope.COLLECTION_PUBLISH, type=ScopeType.odp
            ),
            schema=SchemaFactory(
                type='tag',
                uri='https://odp.saeon.ac.za/schema/tag/generic',
            ),
        ))
    )

    r = client.post(
        f'/collection/{(collection_id := collection_batch[2].id)}/tag',
        json=(collection_tag_2 := dict(
            tag_id='Collection.Publish',
            data={'comment': 'Second tag instance'},
        )))

    if authorized:
        if flag:
            assert_conflict(r, 'Flag has already been set')
            assert_db_tag_state(collection_id, collection_tag_1)
            assert_tag_audit_log()
        else:
            assert_json_tag_result(r, r.json(), collection_tag_2 | dict(flag=False, public=tag.public))
            assert_db_tag_state(collection_id, collection_tag_1, collection_tag_2)
            assert_tag_audit_log(
                dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_2),
            )
    else:
        assert_forbidden(r)
        assert_db_tag_state(collection_id, collection_tag_1)
        assert_tag_audit_log()

    assert_db_state(collection_batch)
