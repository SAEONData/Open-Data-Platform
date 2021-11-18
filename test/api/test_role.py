from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Role
from test.api import assert_empty_result, assert_forbidden, all_scopes, all_scopes_excluding
from test.factories import RoleFactory, ScopeFactory, ProviderFactory


@pytest.fixture
def role_batch():
    """Create and commit a batch of Role instances."""
    return [
        RoleFactory(
            scopes=ScopeFactory.create_batch(randint(0, 3)),
            is_provider_role=n in (1, 2) or randint(0, 1),
        )
        for n in range(randint(3, 5))
    ]


def role_build(provider=None, **id):
    """Build and return an uncommitted Role instance.
    Referenced scopes and/or provider are however committed."""
    return RoleFactory.build(
        **id,
        scopes=ScopeFactory.create_batch(randint(0, 3)),
        provider=provider or (provider := ProviderFactory() if randint(0, 1) else None),
        provider_id=provider.id if provider else None,
    )


def scope_ids(role):
    return tuple(scope.id for scope in role.scopes)


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
    assert tuple(json['scope_ids']) == scope_ids(role)


def assert_json_results(response, json, roles):
    """Verify that the API result list matches the given role batch."""
    json.sort(key=lambda j: j['id'])
    roles.sort(key=lambda r: r.id)
    for n, role in enumerate(roles):
        assert_json_result(response, json[n], role)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.ROLE_READ], True),
    ([ODPScope.ROLE_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.ROLE_READ, ODPScope.ROLE_ADMIN), False),
])
def test_list_roles(api, role_batch, scopes, authorized):
    r = api(scopes).get('/role/')
    if authorized:
        assert_json_results(r, r.json(), role_batch)
    else:
        assert_forbidden(r)
    assert_db_state(role_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.ROLE_READ], True),
    ([ODPScope.ROLE_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.ROLE_READ, ODPScope.ROLE_ADMIN), False),
])
def test_list_roles_with_provider_specific_api_client(api, role_batch, scopes, authorized):
    api_client_provider = role_batch[2].provider
    assert api_client_provider is not None
    r = api(scopes, api_client_provider).get('/role/')
    if authorized:
        assert_json_results(r, r.json(), [role_batch[2]])
    else:
        assert_forbidden(r)
    assert_db_state(role_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.ROLE_READ], True),
    ([ODPScope.ROLE_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.ROLE_READ, ODPScope.ROLE_ADMIN), False),
])
def test_get_role(api, role_batch, scopes, authorized):
    r = api(scopes).get(f'/role/{role_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), role_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(role_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.ROLE_READ], True, True),
    ([ODPScope.ROLE_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.ROLE_READ, ODPScope.ROLE_ADMIN), True, False),
])
def test_get_role_with_provider_specific_api_client(api, role_batch, scopes, matching_provider, authorized):
    api_client_provider = role_batch[2].provider if matching_provider else role_batch[1].provider
    assert api_client_provider is not None
    r = api(scopes, api_client_provider).get(f'/role/{role_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), role_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(role_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.ROLE_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.ROLE_ADMIN), False),
])
def test_create_role(api, role_batch, scopes, authorized):
    modified_role_batch = role_batch + [role := role_build()]
    r = api(scopes).post('/role/', json=dict(
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


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.ROLE_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.ROLE_ADMIN), True, False),
])
def test_create_role_with_provider_specific_api_client(api, role_batch, scopes, matching_provider, authorized):
    api_client_provider = role_batch[2].provider if matching_provider else role_batch[1].provider
    assert api_client_provider is not None
    modified_role_batch = role_batch + [role := role_build(
        provider=role_batch[2].provider
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


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.ROLE_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.ROLE_ADMIN), False),
])
def test_update_role(api, role_batch, scopes, authorized):
    modified_role_batch = role_batch.copy()
    modified_role_batch[2] = (role := role_build(id=role_batch[2].id))
    r = api(scopes).put('/role/', json=dict(
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


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.ROLE_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.ROLE_ADMIN), True, False),
])
def test_update_role_with_provider_specific_api_client(api, role_batch, scopes, matching_provider, authorized):
    api_client_provider = role_batch[2].provider if matching_provider else role_batch[1].provider
    assert api_client_provider is not None
    modified_role_batch = role_batch.copy()
    modified_role_batch[2] = (role := role_build(
        id=role_batch[2].id,
        provider=role_batch[2].provider,
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


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.ROLE_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.ROLE_ADMIN), False),
])
def test_delete_role(api, role_batch, scopes, authorized):
    modified_role_batch = role_batch.copy()
    del modified_role_batch[2]
    r = api(scopes).delete(f'/role/{role_batch[2].id}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_role_batch)
    else:
        assert_forbidden(r)
        assert_db_state(role_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.ROLE_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.ROLE_ADMIN), True, False),
])
def test_delete_role_with_provider_specific_api_client(api, role_batch, scopes, matching_provider, authorized):
    api_client_provider = role_batch[2].provider if matching_provider else role_batch[1].provider
    assert api_client_provider is not None
    modified_role_batch = role_batch.copy()
    del modified_role_batch[2]
    r = api(scopes, api_client_provider).delete(f'/role/{role_batch[2].id}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_role_batch)
    else:
        assert_forbidden(r)
        assert_db_state(role_batch)
