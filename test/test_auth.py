from odp.lib.auth import get_user_access, UserAccess
from test.factories import ScopeFactory, ClientFactory, RoleFactory, UserFactory


def test_platform_roles():
    scopes = ScopeFactory.create_batch(8)
    client = ClientFactory(scopes=scopes[1:7])
    role1 = RoleFactory(scopes=scopes[:3])
    role2 = RoleFactory(scopes=scopes[5:])
    user = UserFactory(roles=(role1, role2))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scope.id: '*'
        for n, scope in enumerate(scopes)
        if n in (1, 2, 5, 6)
    })
    assert actual_user_access == expected_user_access


def test_provider_roles():
    scopes = ScopeFactory.create_batch(8)
    client = ClientFactory(scopes=scopes[1:7])
    role1 = RoleFactory(scopes=scopes[:5], is_provider_role=True)
    role2 = RoleFactory(scopes=scopes[3:], is_provider_role=True)
    user = UserFactory(roles=(role1, role2))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scope.id: {role1.provider_id}
        for n, scope in enumerate(scopes)
        if n in (1, 2)
    } | {
        scope.id: {role1.provider_id, role2.provider_id}
        for n, scope in enumerate(scopes)
        if n in (3, 4)
    } | {
        scope.id: {role2.provider_id}
        for n, scope in enumerate(scopes)
        if n in (5, 6)
    })
    assert actual_user_access == expected_user_access


def test_platform_provider_role_mix():
    scopes = ScopeFactory.create_batch(8)
    client = ClientFactory(scopes=scopes[1:7])
    role1 = RoleFactory(scopes=scopes[:5])
    role2 = RoleFactory(scopes=scopes[3:], is_provider_role=True)
    user = UserFactory(roles=(role1, role2))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scope.id: '*'
        for n, scope in enumerate(scopes)
        if n in (1, 2, 3, 4)
    } | {
        scope.id: {role2.provider_id}
        for n, scope in enumerate(scopes)
        if n in (5, 6)
    })
    assert actual_user_access == expected_user_access


def test_provider_client():
    scopes = ScopeFactory.create_batch(8)
    client = ClientFactory(scopes=scopes[1:7], is_provider_client=True)
    role1 = RoleFactory(scopes=scopes[:3])
    role2 = RoleFactory(scopes=scopes[5:])
    user = UserFactory(roles=(role1, role2))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scope.id: {client.provider_id}
        for n, scope in enumerate(scopes)
        if n in (1, 2, 5, 6)
    })
    assert actual_user_access == expected_user_access


def test_provider_client_platform_provider_role_mix():
    scopes = ScopeFactory.create_batch(8)
    client = ClientFactory(scopes=scopes[1:7], is_provider_client=True)
    role1 = RoleFactory(scopes=scopes[:3])
    role2 = RoleFactory(scopes=scopes[3:5], is_provider_role=True)
    role3 = RoleFactory(scopes=scopes[5:], provider=client.provider)
    user = UserFactory(roles=(role1, role2, role3))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scope.id: {client.provider_id}
        for n, scope in enumerate(scopes)
        if n in (1, 2, 5, 6)
    })
    assert actual_user_access == expected_user_access
