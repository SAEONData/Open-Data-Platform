from random import choice, randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Role
from test.api import ProviderAuth, all_scopes, all_scopes_excluding, assert_empty_result, assert_forbidden
from test.factories import ProviderFactory, RoleFactory, ScopeFactory


@pytest.fixture
def role_batch():
    """Create and commit a batch of Role instances."""
    return [
        RoleFactory(
            scopes=ScopeFactory.create_batch(randint(0, 3), type=choice(('odp', 'client'))),
            is_provider_role=n in (1, 2) or randint(0, 1),
        )
        for n in range(randint(3, 5))
    ]


def role_build(provider=None, **id):
    """Build and return an uncommitted Role instance.
    Referenced scopes and/or provider are however committed."""
    return RoleFactory.build(
        **id,
        scopes=ScopeFactory.create_batch(randint(0, 3), type=choice(('odp', 'client'))),
        provider=provider or (provider := ProviderFactory() if randint(0, 1) else None),
        provider_id=provider.id if provider else None,
    )


def scope_ids(role):
    return tuple(sorted(scope.id for scope in role.scopes))


def assert_db_state(roles):
    """Verify that the DB role table contains the given role batch."""
    Session.expire_all()
    result = Session.execute(select(Role)).scalars().all()
    assert set((row.id, scope_ids(row), row.provider_id) for row in result) \
           == set((role.id, scope_ids(role), role.provider_id) for role in roles)


def assert_json_result(response, json, role):
    """Verify that the API result matches the given role object."""
    assert response.status_code == 200
    assert json['id'] == role.id
    assert json['provider_id'] == role.provider_id
    assert tuple(sorted(json['scope_ids'])) == scope_ids(role)


def assert_json_results(response, json, roles):
    """Verify that the API result list matches the given role batch."""
    items = json['items']
    assert json['total'] == len(items) == len(roles)
    items.sort(key=lambda i: i['id'])
    roles.sort(key=lambda r: r.id)
    for n, role in enumerate(roles):
        assert_json_result(response, items[n], role)


@pytest.mark.parametrize('scopes', [
    [ODPScope.ROLE_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.ROLE_READ),
])
def test_list_roles(api, role_batch, scopes, provider_auth):
    authorized = ODPScope.ROLE_READ in scopes

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = role_batch[2].provider
        expected_result_batch = [role_batch[2]]
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = ProviderFactory()
        expected_result_batch = []
    else:
        api_client_provider = None
        expected_result_batch = role_batch

    r = api(scopes, api_client_provider).get('/role/')

    if authorized:
        assert_json_results(r, r.json(), expected_result_batch)
    else:
        assert_forbidden(r)

    assert_db_state(role_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.ROLE_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.ROLE_READ),
])
def test_get_role(api, role_batch, scopes, provider_auth):
    authorized = ODPScope.ROLE_READ in scopes and \
                 provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = role_batch[2].provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = role_batch[1].provider
    else:
        api_client_provider = None

    r = api(scopes, api_client_provider).get(f'/role/{role_batch[2].id}')

    if authorized:
        assert_json_result(r, r.json(), role_batch[2])
    else:
        assert_forbidden(r)

    assert_db_state(role_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.ROLE_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.ROLE_ADMIN),
])
def test_create_role(api, role_batch, scopes, provider_auth):
    authorized = ODPScope.ROLE_ADMIN in scopes and \
                 provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = role_batch[2].provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = role_batch[1].provider
    else:
        api_client_provider = None

    if provider_auth in (ProviderAuth.MATCH, ProviderAuth.MISMATCH):
        new_role_provider = role_batch[2].provider
    else:
        new_role_provider = None

    modified_role_batch = role_batch + [role := role_build(
        provider=new_role_provider
    )]

    r = api(scopes, api_client_provider).post('/role/', json=dict(
        id=role.id,
        scope_ids=scope_ids(role),
        provider_id=role.provider_id,
    ))

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_role_batch)
    else:
        assert_forbidden(r)
        assert_db_state(role_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.ROLE_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.ROLE_ADMIN),
])
def test_update_role(api, role_batch, scopes, provider_auth):
    authorized = ODPScope.ROLE_ADMIN in scopes and \
                 provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = role_batch[2].provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = role_batch[1].provider
    else:
        api_client_provider = None

    if provider_auth in (ProviderAuth.MATCH, ProviderAuth.MISMATCH):
        modified_role_provider = role_batch[2].provider
    else:
        modified_role_provider = None

    modified_role_batch = role_batch.copy()
    modified_role_batch[2] = (role := role_build(
        id=role_batch[2].id,
        provider=modified_role_provider,
    ))

    r = api(scopes, api_client_provider).put('/role/', json=dict(
        id=role.id,
        scope_ids=scope_ids(role),
        provider_id=role.provider_id,
    ))

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_role_batch)
    else:
        assert_forbidden(r)
        assert_db_state(role_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.ROLE_ADMIN],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.ROLE_ADMIN),
])
def test_delete_role(api, role_batch, scopes, provider_auth):
    authorized = ODPScope.ROLE_ADMIN in scopes and \
                 provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = role_batch[2].provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = role_batch[1].provider
    else:
        api_client_provider = None

    modified_role_batch = role_batch.copy()
    del modified_role_batch[2]

    r = api(scopes, api_client_provider).delete(f'/role/{role_batch[2].id}')

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_role_batch)
    else:
        assert_forbidden(r)
        assert_db_state(role_batch)
