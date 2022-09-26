import re
from datetime import datetime
from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Collection, CollectionAudit, CollectionTag, CollectionTagAudit, Scope, ScopeType
from odplib.formats import DOI_REGEX
from test.api import (CollectionAuth, all_scopes, all_scopes_excluding, assert_conflict, assert_empty_result, assert_forbidden, assert_new_timestamp,
                      assert_not_found, assert_unprocessable)
from test.factories import ClientFactory, CollectionFactory, CollectionTagFactory, ProviderFactory, RoleFactory, SchemaFactory, TagFactory


@pytest.fixture
def collection_batch():
    """Create and commit a batch of Collection instances,
    with associated clients and roles."""
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


def client_ids(collection):
    return tuple(sorted(client.id for client in collection.clients if client.id != 'odp.test'))


def role_ids(collection):
    return tuple(sorted(role.id for role in collection.roles))


def assert_db_state(collections):
    """Verify that the DB collection table contains the given collection batch."""
    Session.expire_all()
    result = Session.execute(select(Collection)).scalars().all()
    result.sort(key=lambda c: c.id)
    collections.sort(key=lambda c: c.id)
    assert len(result) == len(collections)
    for n, row in enumerate(result):
        assert row.id == collections[n].id
        assert row.name == collections[n].name
        assert row.doi_key == collections[n].doi_key
        assert row.provider_id == collections[n].provider_id
        assert_new_timestamp(row.timestamp)
        assert client_ids(row) == client_ids(collections[n])
        assert role_ids(row) == role_ids(collections[n])


def assert_db_tag_state(collection_id, *collection_tags):
    """Verify that the collection_tag table contains the given collection tags."""
    Session.expire_all()
    result = Session.execute(select(CollectionTag)).scalars().all()
    result.sort(key=lambda r: r.timestamp)

    assert len(result) == len(collection_tags)
    for n, row in enumerate(result):
        assert row.collection_id == collection_id
        assert_new_timestamp(row.timestamp)
        if isinstance(collection_tag := collection_tags[n], CollectionTag):
            assert row.tag_id == collection_tag.tag_id
            assert row.user_id == collection_tag.user_id
            assert row.data == collection_tag.data
        else:
            assert row.tag_id == collection_tag['tag_id']
            assert row.user_id is None
            assert row.data == collection_tag['data']


def assert_audit_log(command, collection):
    result = Session.execute(select(CollectionAudit)).scalar_one_or_none()
    assert result.client_id == 'odp.test'
    assert result.user_id is None
    assert result.command == command
    assert_new_timestamp(result.timestamp)
    assert result._id == collection.id
    assert result._name == collection.name
    assert result._doi_key == collection.doi_key
    assert result._provider_id == collection.provider_id


def assert_no_audit_log():
    assert Session.execute(select(CollectionAudit)).first() is None


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
        assert row._user_id == entries[n]['collection_tag'].get('user_id')
        assert row._data == entries[n]['collection_tag']['data']


def assert_json_collection_result(response, json, collection):
    """Verify that the API result matches the given collection object."""
    assert response.status_code == 200
    assert json['id'] == collection.id
    assert json['name'] == collection.name
    assert json['doi_key'] == collection.doi_key
    assert json['provider_id'] == collection.provider_id
    assert tuple(sorted(cid for cid in json['client_ids'] if cid != 'odp.test')) == client_ids(collection)
    assert tuple(sorted(json['role_ids'])) == role_ids(collection)
    assert_new_timestamp(datetime.fromisoformat(json['timestamp']))


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
    assert json['cardinality'] == collection_tag['cardinality']
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
    assert_no_audit_log()


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
    assert_no_audit_log()


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
    assert_no_audit_log()


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
        assert_audit_log('insert', collection)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch)
        assert_no_audit_log()


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
    assert_no_audit_log()


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_ADMIN),
])
def test_update_collection(api, collection_batch, scopes, collection_auth):
    authorized = ODPScope.COLLECTION_ADMIN in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    modified_collection_batch = collection_batch.copy()
    modified_collection_batch[2] = (collection := collection_build(
        id=collection_batch[2].id,
        clients=collection_batch[2].clients,
        roles=collection_batch[2].roles,
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
        assert_audit_log('update', collection)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch)
        assert_no_audit_log()


def test_update_collection_not_found(api, collection_batch, collection_auth):
    scopes = [ODPScope.COLLECTION_ADMIN]
    authorized = collection_auth == CollectionAuth.NONE

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = collection_batch[2]

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

    assert_db_state(collection_batch)
    assert_no_audit_log()


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
    deleted_collection = modified_collection_batch[2]
    del modified_collection_batch[2]

    r = api(scopes, api_client_collection).delete(f'/collection/{(collection_id := collection_batch[2].id)}')

    if authorized:
        assert_empty_result(r)
        # check audit log first because assert_db_state expires the deleted item
        assert_audit_log('delete', deleted_collection)
        assert_db_state(modified_collection_batch)
    else:
        assert_forbidden(r)
        assert_db_state(collection_batch)
        assert_no_audit_log()


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
    assert_no_audit_log()


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
    assert_no_audit_log()


def new_generic_tag(cardinality):
    # we can use any scope; just make it something other than COLLECTION_ADMIN
    return TagFactory(
        type='collection',
        cardinality=cardinality,
        scope=Session.get(
            Scope, (ODPScope.COLLECTION_READ, ScopeType.odp)
        ) or Scope(
            id=ODPScope.COLLECTION_READ, type=ScopeType.odp
        ),
        schema=SchemaFactory(
            type='tag',
            uri='https://odp.saeon.ac.za/schema/tag/generic',
        ),
    )


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_READ],  # the scope we've associated with the generic tag
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_READ),
])
def test_tag_collection(api, collection_batch, scopes, collection_auth, tag_cardinality):
    authorized = ODPScope.COLLECTION_READ in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    client = api(scopes, api_client_collection)
    tag = new_generic_tag(tag_cardinality)

    r = client.post(
        f'/collection/{(collection_id := collection_batch[2].id)}/tag',
        json=(collection_tag_1 := dict(
            tag_id=tag.id,
            data={'comment': 'test1'},
        )))

    if authorized:
        assert_json_tag_result(r, r.json(), collection_tag_1 | dict(cardinality=tag_cardinality, public=tag.public))
        assert_db_tag_state(collection_id, collection_tag_1)
        assert_tag_audit_log(
            dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_1),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(collection_id)
        assert_tag_audit_log()

    r = client.post(
        f'/collection/{(collection_id := collection_batch[2].id)}/tag',
        json=(collection_tag_2 := dict(
            tag_id=tag.id,
            data={'comment': 'test2'},
        )))

    if authorized:
        assert_json_tag_result(r, r.json(), collection_tag_2 | dict(cardinality=tag_cardinality, public=tag.public))
        if tag_cardinality in ('one', 'user'):
            assert_db_tag_state(collection_id, collection_tag_2)
            assert_tag_audit_log(
                dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_1),
                dict(command='update', collection_id=collection_id, collection_tag=collection_tag_2),
            )
        elif tag_cardinality == 'multi':
            assert_db_tag_state(collection_id, collection_tag_1, collection_tag_2)
            assert_tag_audit_log(
                dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_1),
                dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_2),
            )
        else:
            assert False
    else:
        assert_forbidden(r)
        assert_db_tag_state(collection_id)
        assert_tag_audit_log()

    assert_db_state(collection_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes', [
    [ODPScope.COLLECTION_READ],  # the scope we've associated with the generic tag
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.COLLECTION_READ),
])
def test_tag_collection_user_conflict(api, collection_batch, scopes, collection_auth, tag_cardinality):
    authorized = ODPScope.COLLECTION_READ in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    client = api(scopes, api_client_collection)
    tag = new_generic_tag(tag_cardinality)
    collection_tag_1 = CollectionTagFactory(
        collection=collection_batch[2],
        tag=tag,
    )

    r = client.post(
        f'/collection/{(collection_id := collection_batch[2].id)}/tag',
        json=(collection_tag_2 := dict(
            tag_id=tag.id,
            data={'comment': 'test2'},
        )))

    if authorized:
        if tag_cardinality == 'one':
            assert_conflict(r, 'Cannot update a tag set by another user')
            assert_db_tag_state(collection_id, collection_tag_1)
            assert_tag_audit_log()
        elif tag_cardinality in ('user', 'multi'):
            assert_json_tag_result(r, r.json(), collection_tag_2 | dict(cardinality=tag_cardinality, public=tag.public))
            assert_db_tag_state(collection_id, collection_tag_1, collection_tag_2)
            assert_tag_audit_log(
                dict(command='insert', collection_id=collection_id, collection_tag=collection_tag_2),
            )
        else:
            assert False
    else:
        assert_forbidden(r)
        assert_db_tag_state(collection_id, collection_tag_1)
        assert_tag_audit_log()

    assert_db_state(collection_batch)
    assert_no_audit_log()


@pytest.fixture(params=[True, False])
def same_user(request):
    return request.param


@pytest.mark.parametrize('admin_route, scopes', [
    (False, [ODPScope.COLLECTION_READ]),  # the scope we've associated with the generic tag
    (False, []),
    (False, all_scopes),
    (False, all_scopes_excluding(ODPScope.COLLECTION_READ)),
    (True, [ODPScope.COLLECTION_ADMIN]),
    (True, []),
    (True, all_scopes),
    (True, all_scopes_excluding(ODPScope.COLLECTION_ADMIN)),
])
def test_untag_collection(api, collection_batch, admin_route, scopes, collection_auth, tag_cardinality, same_user):
    route = '/collection/admin/' if admin_route else '/collection/'

    authorized = admin_route and ODPScope.COLLECTION_ADMIN in scopes or \
                 not admin_route and ODPScope.COLLECTION_READ in scopes
    authorized = authorized and collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = collection_batch[2]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = collection_batch[1]
    else:
        api_client_collection = None

    client = api(scopes, api_client_collection)
    collection = collection_batch[2]
    collection_tags = CollectionTagFactory.create_batch(randint(1, 3), collection=collection)

    tag = new_generic_tag(tag_cardinality)
    if same_user:
        collection_tag_1 = CollectionTagFactory(
            collection=collection,
            tag=tag,
            user=None,
        )
    else:
        collection_tag_1 = CollectionTagFactory(
            collection=collection,
            tag=tag,
        )
    collection_tag_1_dict = {
        'tag_id': collection_tag_1.tag_id,
        'user_id': collection_tag_1.user_id,
        'data': collection_tag_1.data,
    }

    r = client.delete(f'{route}{collection.id}/tag/{collection_tag_1.id}')

    if authorized:
        if not admin_route and not same_user:
            assert_forbidden(r)
            assert_db_tag_state(collection.id, *collection_tags, collection_tag_1)
            assert_tag_audit_log()
        else:
            assert_empty_result(r)
            assert_db_tag_state(collection.id, *collection_tags)
            assert_tag_audit_log(
                dict(command='delete', collection_id=collection.id, collection_tag=collection_tag_1_dict),
            )
    else:
        assert_forbidden(r)
        assert_db_tag_state(collection.id, *collection_tags, collection_tag_1)
        assert_tag_audit_log()

    assert_db_state(collection_batch)
    assert_no_audit_log()
