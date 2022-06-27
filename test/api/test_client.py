from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Client
from odp.lib.hydra import TokenEndpointAuthMethod
from test.api import CollectionAuth, all_scopes, all_scopes_excluding, assert_conflict, assert_empty_result, assert_forbidden, assert_not_found
from test.factories import ClientFactory, CollectionFactory, ScopeFactory, fake


@pytest.fixture
def client_batch(hydra_admin_api):
    """Create and commit a batch of Client instances, and create
    an OAuth2 client config on Hydra for each."""
    clients = []
    for n in range(randint(3, 5)):
        clients += [client := ClientFactory(
            scopes=(scopes := ScopeFactory.create_batch(randint(1, 3))),
            is_collection_client=n in (1, 2) or randint(0, 1),
        )]
        hydra_admin_api.create_or_update_client(
            client.id,
            name=fake.catch_phrase(),
            secret=fake.password(),
            scope_ids=[s.id for s in scopes],
            grant_types=[],
        )

    return clients


@pytest.fixture(autouse=True)
def delete_hydra_clients(hydra_admin_api):
    """Delete Hydra client configs after each test."""
    try:
        yield
    finally:
        for hydra_client in hydra_admin_api.list_clients():
            if hydra_client.id != 'odp.test':
                hydra_admin_api.delete_client(hydra_client.id)


def client_build(collection=None, **id):
    """Build and return an uncommitted Client instance.
    Referenced scopes and/or collection are however committed."""
    return ClientFactory.build(
        **id,
        scopes=ScopeFactory.create_batch(randint(1, 3)),
        collection=collection or (collection := CollectionFactory() if randint(0, 1) else None),
        collection_id=collection.id if collection else None,
    )


def scope_ids(client):
    return tuple(sorted(scope.id for scope in client.scopes))


def assert_db_state(clients):
    """Verify that the DB client table contains the given client batch."""
    Session.expire_all()
    result = Session.execute(select(Client).where(Client.id != 'odp.test')).scalars().all()
    assert set((row.id, scope_ids(row), row.collection_id) for row in result) \
           == set((client.id, scope_ids(client), client.collection_id) for client in clients)


def assert_json_result(response, json, client):
    """Verify that the API result matches the given client object.

    TODO: test Hydra client config values
    """
    assert response.status_code == 200
    assert json['id'] == client.id
    assert json['collection_id'] == client.collection_id
    assert tuple(sorted(json['scope_ids'])) == scope_ids(client)


def assert_json_results(response, json, clients):
    """Verify that the API result list matches the given client batch."""
    items = [j for j in json['items'] if j['id'] != 'odp.test']
    assert json['total'] - 1 == len(items) == len(clients)
    items.sort(key=lambda i: i['id'])
    clients.sort(key=lambda c: c.id)
    for n, client in enumerate(clients):
        assert_json_result(response, items[n], client)


@pytest.mark.parametrize('scopes', [
    [ODPScope.CLIENT_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.CLIENT_READ),
])
def test_list_clients(api, client_batch, scopes, collection_auth):
    authorized = ODPScope.CLIENT_READ in scopes

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = client_batch[2].collection
        expected_result_batch = [client_batch[2]]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = CollectionFactory()
        expected_result_batch = []
    else:
        api_client_collection = None
        expected_result_batch = client_batch

    r = api(scopes, api_client_collection).get('/client/')

    if authorized:
        assert_json_results(r, r.json(), expected_result_batch)
    else:
        assert_forbidden(r)

    assert_db_state(client_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.CLIENT_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.CLIENT_READ),
])
def test_get_client(api, client_batch, scopes, collection_auth):
    authorized = ODPScope.CLIENT_READ in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = client_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = client_batch[1].collection
    else:
        api_client_collection = None

    r = api(scopes, api_client_collection).get(f'/client/{client_batch[2].id}')

    if authorized:
        assert_json_result(r, r.json(), client_batch[2])
    else:
        assert_forbidden(r)

    assert_db_state(client_batch)


def test_get_client_not_found(api, client_batch, collection_auth):
    scopes = [ODPScope.CLIENT_READ]

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = client_batch[2].collection

    r = api(scopes, api_client_collection).get('/client/foo')

    # we can't get a forbidden, regardless of collection auth, because
    # if the client is not found, there is no collection to compare with
    assert_not_found(r)
    assert_db_state(client_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.CLIENT_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.CLIENT_ADMIN),
])
def test_create_client(api, client_batch, scopes, collection_auth):
    authorized = ODPScope.CLIENT_ADMIN in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = client_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = client_batch[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        new_client_collection = client_batch[2].collection
    else:
        new_client_collection = None

    modified_client_batch = client_batch + [client := client_build(
        collection=new_client_collection
    )]

    r = api(scopes, api_client_collection).post('/client/', json=dict(
        id=client.id,
        name=fake.catch_phrase(),
        secret=fake.password(),
        scope_ids=scope_ids(client),
        collection_id=client.collection_id,
        grant_types=[],
        response_types=[],
        redirect_uris=[],
        post_logout_redirect_uris=[],
        token_endpoint_auth_method=TokenEndpointAuthMethod.CLIENT_SECRET_BASIC,
        allowed_cors_origins=[],
    ))

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_client_batch)
    else:
        assert_forbidden(r)
        assert_db_state(client_batch)


def test_create_client_conflict(api, client_batch, collection_auth):
    scopes = [ODPScope.CLIENT_ADMIN]
    authorized = collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = client_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = client_batch[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        new_client_collection = client_batch[2].collection
    else:
        new_client_collection = None

    client = client_build(
        id=client_batch[2].id,
        collection=new_client_collection,
    )

    r = api(scopes, api_client_collection).post('/client/', json=dict(
        id=client.id,
        name=fake.catch_phrase(),
        secret=fake.password(),
        scope_ids=scope_ids(client),
        collection_id=client.collection_id,
        grant_types=[],
        response_types=[],
        redirect_uris=[],
        post_logout_redirect_uris=[],
        token_endpoint_auth_method=TokenEndpointAuthMethod.CLIENT_SECRET_BASIC,
        allowed_cors_origins=[],
    ))

    if authorized:
        assert_conflict(r, 'Client id is already in use')
    else:
        assert_forbidden(r)

    assert_db_state(client_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.CLIENT_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.CLIENT_ADMIN),
])
def test_update_client(api, client_batch, scopes, collection_auth):
    authorized = ODPScope.CLIENT_ADMIN in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = client_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = client_batch[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        modified_client_collection = client_batch[2].collection
    else:
        modified_client_collection = None

    modified_client_batch = client_batch.copy()
    modified_client_batch[2] = (client := client_build(
        id=client_batch[2].id,
        collection=modified_client_collection,
    ))

    r = api(scopes, api_client_collection).put('/client/', json=dict(
        id=client.id,
        name=fake.catch_phrase(),
        secret=fake.password(),
        scope_ids=scope_ids(client),
        collection_id=client.collection_id,
        grant_types=[],
        response_types=[],
        redirect_uris=[],
        post_logout_redirect_uris=[],
        token_endpoint_auth_method=TokenEndpointAuthMethod.CLIENT_SECRET_BASIC,
        allowed_cors_origins=[],
    ))

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_client_batch)
    else:
        assert_forbidden(r)
        assert_db_state(client_batch)


def test_update_client_not_found(api, client_batch, collection_auth):
    scopes = [ODPScope.CLIENT_ADMIN]
    authorized = collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = client_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = client_batch[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        modified_client_collection = client_batch[2].collection
    else:
        modified_client_collection = None

    client = client_build(
        id='foo',
        collection=modified_client_collection,
    )

    r = api(scopes, api_client_collection).put('/client/', json=dict(
        id=client.id,
        name=fake.catch_phrase(),
        secret=fake.password(),
        scope_ids=scope_ids(client),
        collection_id=client.collection_id,
        grant_types=[],
        response_types=[],
        redirect_uris=[],
        post_logout_redirect_uris=[],
        token_endpoint_auth_method=TokenEndpointAuthMethod.CLIENT_SECRET_BASIC,
        allowed_cors_origins=[],
    ))

    if authorized:
        assert_not_found(r)
    else:
        assert_forbidden(r)

    assert_db_state(client_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.CLIENT_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.CLIENT_ADMIN),
])
def test_delete_client(api, client_batch, scopes, collection_auth):
    authorized = ODPScope.CLIENT_ADMIN in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = client_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = client_batch[1].collection
    else:
        api_client_collection = None

    modified_client_batch = client_batch.copy()
    del modified_client_batch[2]

    r = api(scopes, api_client_collection).delete(f'/client/{client_batch[2].id}')

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_client_batch)
    else:
        assert_forbidden(r)
        assert_db_state(client_batch)


def test_delete_client_not_found(api, client_batch, collection_auth):
    scopes = [ODPScope.CLIENT_ADMIN]

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = client_batch[2].collection

    r = api(scopes, api_client_collection).delete('/client/foo')

    # we can't get a forbidden, regardless of collection auth, because
    # if the client is not found, there is no collection to compare with
    assert_not_found(r)
    assert_db_state(client_batch)
