from odp.lib.auth import get_user_access, ScopeContext, UserAccess
from test.factories import ScopeFactory, ClientFactory, RoleFactory, UserFactory


def test_unpinned_role():
    scopes = ScopeFactory.create_batch(4)
    client = ClientFactory(scopes=scopes[:3])
    role = RoleFactory(scopes=scopes[1:])
    user = UserFactory(roles=(role,))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scope.id: '*' for scope in scopes[1:3]
    })
    assert actual_user_access == expected_user_access


def test_provider_role():
    scopes = ScopeFactory.create_batch(4)
    client = ClientFactory(scopes=scopes[:3])
    role = RoleFactory(scopes=scopes[1:], is_provider_role=True)
    user = UserFactory(roles=(role,))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scope.id: (ScopeContext(projects='*', providers={role.provider.key}))
        for scope in scopes[1:3]
    })
    assert actual_user_access == expected_user_access


def test_project_role():
    scopes = ScopeFactory.create_batch(4)
    client = ClientFactory(scopes=scopes[:3])
    role = RoleFactory(scopes=scopes[1:], is_project_role=True)
    user = UserFactory(roles=(role,))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scope.id: (ScopeContext(projects={role.project.key}, providers='*'))
        for scope in scopes[1:3]
    })
    assert actual_user_access == expected_user_access


def test_mixed_roles():
    """Test user access calculation when multiple roles with different
    limitations and overlapping scope assignments are granted to a user.

    Configuration:
    Scope   Client  Role1   Role2   Role3   Role4   Role5
                     prj1   prv2  prj3+prv3  prv4
      0               x
      1       x       x
      2       x       x               x
      3       x       x       x       x
      4       x       x       x       x               x
      5       x               x       x               x
      6       x               x               x
      7                       x               x

    Expected result:
    Scope   Prj     Prv
      1      1       *
      2     1,3      3
      3     1,3     2,3
      4      *       *
      5      *       *
      6      *      2,4
    """
    scopes = ScopeFactory.create_batch(8)
    client = ClientFactory(scopes=scopes[1:7])
    role1 = RoleFactory(scopes=scopes[:5], is_project_role=True)
    role2 = RoleFactory(scopes=scopes[3:], is_provider_role=True)
    role3 = RoleFactory(scopes=scopes[2:6], is_project_role=True, is_provider_role=True)
    role4 = RoleFactory(scopes=scopes[6:], is_provider_role=True)
    role5 = RoleFactory(scopes=scopes[4:6])
    user = UserFactory(roles=(role1, role2, role3, role4, role5))
    actual_user_access = get_user_access(user.id, client.id)
    expected_user_access = UserAccess(scopes={
        scopes[1].id: ScopeContext(projects={role1.project.key}, providers='*'),
        scopes[2].id: ScopeContext(projects={role1.project.key, role3.project.key}, providers={role3.provider.key}),
        scopes[3].id: ScopeContext(projects={role1.project.key, role3.project.key}, providers={role2.provider.key, role3.provider.key}),
        scopes[4].id: '*',
        scopes[5].id: '*',
        scopes[6].id: ScopeContext(projects='*', providers={role2.provider.key, role4.provider.key}),
    })
    assert actual_user_access == expected_user_access
