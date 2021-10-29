from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Client
from test.api import assert_empty_result, assert_forbidden
from test.factories import ClientFactory, ScopeFactory, ProviderFactory


@pytest.fixture
def client_batch():
    """Create and commit a batch of Client instances."""
    return [
        ClientFactory(
            scopes=ScopeFactory.create_batch(randint(0, 3)),
            is_provider_client=randint(0, 1),
        )
        for _ in range(randint(3, 5))
    ]


def client_build(**id):
    """Build and return an uncommitted Client instance.
    Referenced scopes and/or provider are however committed."""
    return ClientFactory.build(
        **id,
        scopes=ScopeFactory.create_batch(randint(0, 3)),
        provider=(provider := ProviderFactory() if randint(0, 1) else None),
        provider_id=provider.id if provider else None,
    )


def scope_ids(client):
    return tuple(scope.id for scope in client.scopes)


def assert_db_state(clients):
    """Verify that the DB client table contains the given client batch."""
    Session.expire_all()
    result = Session.execute(select(Client).where(Client.id != 'odp.test')).scalars().all()
    assert set((row.id, row.name, scope_ids(row), row.provider_id) for row in result) \
           == set((client.id, client.name, scope_ids(client), client.provider_id) for client in clients)


def assert_json_result(response, json, client):
    """Verify that the API result matches the given client object."""
    assert response.status_code == 200
    assert json['id'] == client.id
    assert json['name'] == client.name
    assert json['provider_id'] == client.provider_id
    assert tuple(json['scope_ids']) == scope_ids(client)


def assert_json_results(response, json, clients):
    """Verify that the API result list matches the given client batch."""
    json = [j for j in json if j['id'] != 'odp.test']
    for n, client in enumerate(sorted(clients, key=lambda c: c.id)):
        assert_json_result(response, json[n], client)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.CLIENT_READ], True),
    ([ODPScope.CLIENT_ADMIN], False),
    ([ODPScope.CLIENT_ADMIN, ODPScope.CLIENT_READ], True),
])
def test_list_clients(api, client_batch, scopes, authorized):
    r = api(scopes).get('/client/')
    if authorized:
        assert_json_results(r, r.json(), client_batch)
    else:
        assert_forbidden(r)
    assert_db_state(client_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.CLIENT_READ], True),
    ([ODPScope.CLIENT_ADMIN], False),
    ([ODPScope.CLIENT_ADMIN, ODPScope.CLIENT_READ], True),
])
def test_get_client(api, client_batch, scopes, authorized):
    r = api(scopes).get(f'/client/{client_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), client_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(client_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.CLIENT_READ], False),
    ([ODPScope.CLIENT_ADMIN], True),
    ([ODPScope.CLIENT_ADMIN, ODPScope.CLIENT_READ], True),
])
def test_create_client(api, client_batch, scopes, authorized):
    modified_client_batch = client_batch + [client := client_build()]
    r = api(scopes).post('/client/', json=dict(
        id=client.id,
        name=client.name,
        scope_ids=scope_ids(client),
        provider_id=client.provider_id,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_client_batch)
    else:
        assert_forbidden(r)
        assert_db_state(client_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.CLIENT_READ], False),
    ([ODPScope.CLIENT_ADMIN], True),
    ([ODPScope.CLIENT_ADMIN, ODPScope.CLIENT_READ], True),
])
def test_update_client(api, client_batch, scopes, authorized):
    modified_client_batch = client_batch.copy()
    modified_client_batch[2] = (client := client_build(id=client_batch[2].id))
    r = api(scopes).put('/client/', json=dict(
        id=client.id,
        name=client.name,
        scope_ids=scope_ids(client),
        provider_id=client.provider_id,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_client_batch)
    else:
        assert_forbidden(r)
        assert_db_state(client_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.CLIENT_READ], False),
    ([ODPScope.CLIENT_ADMIN], True),
    ([ODPScope.CLIENT_ADMIN, ODPScope.CLIENT_READ], True),
])
def test_delete_client(api, client_batch, scopes, authorized):
    modified_client_batch = client_batch.copy()
    del modified_client_batch[2]
    r = api(scopes).delete(f'/client/{client_batch[2].id}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_client_batch)
    else:
        assert_forbidden(r)
        assert_db_state(client_batch)