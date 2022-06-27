from odp.lib.auth import get_user_permissions, get_client_permissions, Permissions, get_user_info, UserInfo
from test.factories import ScopeFactory, ClientFactory, RoleFactory, UserFactory


def assert_compare(expected: Permissions, actual: Permissions):
    if expected == actual:
        return

    expected = {
        scope_id: set(collection_ids) if collection_ids != '*' else '*'
        for scope_id, collection_ids in expected.items()
    }
    actual = {
        scope_id: set(collection_ids) if collection_ids != '*' else '*'
        for scope_id, collection_ids in actual.items()
    }
    assert expected == actual


def test_platform_roles():
    scopes = ScopeFactory.create_batch(8, type='odp')
    client = ClientFactory(scopes=scopes[1:7])
    role1 = RoleFactory(scopes=scopes[:3])
    role2 = RoleFactory(scopes=scopes[5:])
    user = UserFactory(roles=(role1, role2))

    actual_user_perm = get_user_permissions(user.id, client.id)
    expected_user_perm = {
        scope.id: '*'
        for n, scope in enumerate(scopes)
        if n in (1, 2, 5, 6)
    }
    assert_compare(expected_user_perm, actual_user_perm)

    actual_client_perm = get_client_permissions(client.id)
    expected_client_perm = {
        scope.id: '*'
        for scope in scopes[1:7]
    }
    assert_compare(expected_client_perm, actual_client_perm)


def test_collection_roles():
    scopes = ScopeFactory.create_batch(8, type='odp')
    client = ClientFactory(scopes=scopes[1:7])
    role1 = RoleFactory(scopes=scopes[:5], is_collection_role=True)
    role2 = RoleFactory(scopes=scopes[3:], is_collection_role=True)
    user = UserFactory(roles=(role1, role2))

    actual_user_perm = get_user_permissions(user.id, client.id)
    expected_user_perm = {
        scope.id: [role1.collection_id]
        for n, scope in enumerate(scopes)
        if n in (1, 2)
    } | {
        scope.id: [role1.collection_id, role2.collection_id]
        for n, scope in enumerate(scopes)
        if n in (3, 4)
    } | {
        scope.id: [role2.collection_id]
        for n, scope in enumerate(scopes)
        if n in (5, 6)
    }
    assert_compare(expected_user_perm, actual_user_perm)

    actual_client_perm = get_client_permissions(client.id)
    expected_client_perm = {
        scope.id: '*'
        for scope in scopes[1:7]
    }
    assert_compare(expected_client_perm, actual_client_perm)


def test_platform_collection_role_mix():
    scopes = ScopeFactory.create_batch(8, type='odp')
    client = ClientFactory(scopes=scopes[1:7])
    role1 = RoleFactory(scopes=scopes[:4])
    role2 = RoleFactory(scopes=scopes[3:], is_collection_role=True)
    role3 = RoleFactory(scopes=scopes[5:], is_collection_role=True)
    user = UserFactory(roles=(role1, role2, role3))

    actual_user_perm = get_user_permissions(user.id, client.id)
    expected_user_perm = {
        scope.id: '*'
        for n, scope in enumerate(scopes)
        if n in (1, 2, 3)
    } | {
        scope.id: [role2.collection_id]
        for n, scope in enumerate(scopes)
        if n == 4
    } | {
        scope.id: [role2.collection_id, role3.collection_id]
        for n, scope in enumerate(scopes)
        if n in (5, 6)
    }
    assert_compare(expected_user_perm, actual_user_perm)

    actual_client_perm = get_client_permissions(client.id)
    expected_client_perm = {
        scope.id: '*'
        for scope in scopes[1:7]
    }
    assert_compare(expected_client_perm, actual_client_perm)


def test_collection_client():
    scopes = ScopeFactory.create_batch(8, type='odp')
    client = ClientFactory(scopes=scopes[1:7], is_collection_client=True)
    role1 = RoleFactory(scopes=scopes[:3])
    role2 = RoleFactory(scopes=scopes[5:])
    user = UserFactory(roles=(role1, role2))

    actual_user_perm = get_user_permissions(user.id, client.id)
    expected_user_perm = {
        scope.id: [client.collection_id]
        for n, scope in enumerate(scopes)
        if n in (1, 2, 5, 6)
    }
    assert_compare(expected_user_perm, actual_user_perm)

    actual_client_perm = get_client_permissions(client.id)
    expected_client_perm = {
        scope.id: [client.collection_id]
        for scope in scopes[1:7]
    }
    assert_compare(expected_client_perm, actual_client_perm)


def test_collection_client_platform_collection_role_mix():
    scopes = ScopeFactory.create_batch(8, type='odp')
    client = ClientFactory(scopes=scopes[1:7], is_collection_client=True)
    role1 = RoleFactory(scopes=scopes[:3])
    role2 = RoleFactory(scopes=scopes[3:5], is_collection_role=True)
    role3 = RoleFactory(scopes=scopes[5:], collection=client.collection)
    user = UserFactory(roles=(role1, role2, role3))

    actual_user_perm = get_user_permissions(user.id, client.id)
    expected_user_perm = {
        scope.id: [client.collection_id]
        for n, scope in enumerate(scopes)
        if n in (1, 2, 5, 6)
    }
    assert_compare(expected_user_perm, actual_user_perm)

    actual_client_perm = get_client_permissions(client.id)
    expected_client_perm = {
        scope.id: [client.collection_id]
        for scope in scopes[1:7]
    }
    assert_compare(expected_client_perm, actual_client_perm)


def test_user_info():
    client = ClientFactory()
    role1 = RoleFactory()
    role2 = RoleFactory()
    user = UserFactory(roles=(role1, role2))

    actual_user_info = get_user_info(user.id, client.id)
    expected_user_info = UserInfo(
        sub=user.id,
        email=user.email,
        email_verified=user.verified,
        name=user.name,
        picture=None,
        roles=[role1.id, role2.id],
    )
    assert expected_user_info == actual_user_info


def test_user_info_collection_roles():
    client = ClientFactory()
    role1 = RoleFactory()
    role2 = RoleFactory(is_collection_role=True)
    role3 = RoleFactory(is_collection_role=True)
    user = UserFactory(roles=(role1, role2, role3))

    actual_user_info = get_user_info(user.id, client.id)
    expected_user_info = UserInfo(
        sub=user.id,
        email=user.email,
        email_verified=user.verified,
        name=user.name,
        picture=None,
        roles=[role1.id, role2.id, role3.id],
    )
    assert expected_user_info == actual_user_info


def test_user_info_collection_roles_and_client():
    client = ClientFactory(is_collection_client=True)
    role1 = RoleFactory()
    role2 = RoleFactory(collection=client.collection)
    role3 = RoleFactory(collection=client.collection)
    role4 = RoleFactory(is_collection_role=True)
    user = UserFactory(roles=(role1, role2, role3, role4))

    actual_user_info = get_user_info(user.id, client.id)
    expected_user_info = UserInfo(
        sub=user.id,
        email=user.email,
        email_verified=user.verified,
        name=user.name,
        picture=None,
        roles=[role1.id, role2.id, role3.id],
    )
    assert expected_user_info == actual_user_info
