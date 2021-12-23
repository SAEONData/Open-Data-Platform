from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Provider
from test.api import assert_empty_result, assert_forbidden, all_scopes, all_scopes_excluding
from test.factories import ProviderFactory, CollectionFactory, ClientFactory, RoleFactory


@pytest.fixture
def provider_batch():
    """Create and commit a batch of Provider instances,
    with associated collections, clients and roles."""
    providers = [ProviderFactory() for _ in range(randint(3, 5))]
    for provider in providers:
        CollectionFactory.create_batch(randint(0, 3), provider=provider)
        ClientFactory.create_batch(randint(0, 3), provider=provider)
        RoleFactory.create_batch(randint(0, 3), provider=provider)
    return providers


def provider_build(**kwargs):
    """Build and return an uncommitted Provider instance."""
    return ProviderFactory.build(**kwargs)


def collection_ids(provider):
    return tuple(collection.id for collection in provider.collections)


def client_ids(provider):
    return tuple(client.id for client in provider.clients if client.id != 'odp.test')


def role_ids(provider):
    return tuple(role.id for role in provider.roles)


def assert_db_state(providers):
    """Verify that the DB provider table contains the given provider batch."""
    Session.expire_all()
    result = Session.execute(select(Provider)).scalars().all()
    assert set((row.id, row.name, collection_ids(row), client_ids(row), role_ids(row)) for row in result) \
           == set((provider.id, provider.name, collection_ids(provider), client_ids(provider), role_ids(provider)) for provider in providers)


def assert_json_result(response, json, provider):
    """Verify that the API result matches the given provider object."""
    assert response.status_code == 200
    assert json['id'] == provider.id
    assert json['name'] == provider.name
    assert tuple(json['collection_ids']) == collection_ids(provider)
    assert tuple(j for j in json['client_ids'] if j != 'odp.test') == client_ids(provider)
    assert tuple(json['role_ids']) == role_ids(provider)


def assert_json_results(response, json, providers):
    """Verify that the API result list matches the given provider batch."""
    items = json['items']
    assert json['total'] == len(items) == len(providers)
    items.sort(key=lambda i: i['id'])
    providers.sort(key=lambda p: p.id)
    for n, provider in enumerate(providers):
        assert_json_result(response, items[n], provider)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROVIDER_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROVIDER_READ), False),
])
def test_list_providers(api, provider_batch, scopes, authorized):
    r = api(scopes).get('/provider/')
    if authorized:
        assert_json_results(r, r.json(), provider_batch)
    else:
        assert_forbidden(r)
    assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROVIDER_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROVIDER_READ), False),
])
def test_list_providers_with_provider_specific_api_client(api, provider_batch, scopes, authorized):
    api_client_provider = provider_batch[2]
    r = api(scopes, api_client_provider).get('/provider/')
    if authorized:
        assert_json_results(r, r.json(), [provider_batch[2]])
    else:
        assert_forbidden(r)
    assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROVIDER_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROVIDER_READ), False),
])
def test_get_provider(api, provider_batch, scopes, authorized):
    r = api(scopes).get(f'/provider/{provider_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), provider_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.PROVIDER_READ], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.PROVIDER_READ), True, False),
])
def test_get_provider_with_provider_specific_api_client(api, provider_batch, scopes, matching_provider, authorized):
    api_client_provider = provider_batch[2] if matching_provider else provider_batch[1]
    r = api(scopes, api_client_provider).get(f'/provider/{provider_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), provider_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROVIDER_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROVIDER_ADMIN), False),
])
def test_create_provider(api, provider_batch, scopes, authorized):
    modified_provider_batch = provider_batch + [provider := provider_build()]
    r = api(scopes).post('/provider/', json=dict(
        id=provider.id,
        name=provider.name,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_provider_batch)
    else:
        assert_forbidden(r)
        assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROVIDER_ADMIN], False),
    ([], False),
    (all_scopes, False),
])
def test_create_provider_with_provider_specific_api_client(api, provider_batch, scopes, authorized):
    api_client_provider = provider_batch[2]
    modified_provider_batch = provider_batch + [provider := provider_build()]
    r = api(scopes, api_client_provider).post('/provider/', json=dict(
        id=provider.id,
        name=provider.name,
    ))
    assert_forbidden(r)
    assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROVIDER_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROVIDER_ADMIN), False),
])
def test_update_provider(api, provider_batch, scopes, authorized):
    modified_provider_batch = provider_batch.copy()
    modified_provider_batch[2] = (provider := provider_build(
        id=provider_batch[2].id,
        collections=provider_batch[2].collections,
        clients=provider_batch[2].clients,
        roles=provider_batch[2].roles,
    ))
    r = api(scopes).put('/provider/', json=dict(
        id=provider.id,
        name=provider.name,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_provider_batch)
    else:
        assert_forbidden(r)
        assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.PROVIDER_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.PROVIDER_ADMIN), True, False),
])
def test_update_provider_with_provider_specific_api_client(api, provider_batch, scopes, matching_provider, authorized):
    api_client_provider = provider_batch[2] if matching_provider else provider_batch[1]
    modified_provider_batch = provider_batch.copy()
    modified_provider_batch[2] = (provider := provider_build(
        id=provider_batch[2].id,
        collections=provider_batch[2].collections,
        clients=provider_batch[2].clients,
        roles=provider_batch[2].roles,
    ))
    r = api(scopes, api_client_provider).put('/provider/', json=dict(
        id=provider.id,
        name=provider.name,
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_provider_batch)
    else:
        assert_forbidden(r)
        assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROVIDER_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROVIDER_ADMIN), False),
])
def test_delete_provider(api, provider_batch, scopes, authorized):
    modified_provider_batch = provider_batch.copy()
    del modified_provider_batch[2]
    r = api(scopes).delete(f'/provider/{provider_batch[2].id}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_provider_batch)
    else:
        assert_forbidden(r)
        assert_db_state(provider_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.PROVIDER_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.PROVIDER_ADMIN), True, False),
])
def test_delete_provider_with_provider_specific_api_client(api, provider_batch, scopes, matching_provider, authorized):
    api_client_provider = provider_batch[2] if matching_provider else provider_batch[1]
    modified_provider_batch = provider_batch.copy()
    del modified_provider_batch[2]
    r = api(scopes, api_client_provider).delete(f'/provider/{provider_batch[2].id}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_provider_batch)
    else:
        assert_forbidden(r)
        assert_db_state(provider_batch)
