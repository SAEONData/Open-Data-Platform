from odp.api.models.auth import UserAccess, ScopeContext
from odp.lib.auth import get_user_access
from test.factories import ScopeFactory, ClientFactory, RoleFactory, UserFactory


def test_unpinned_role():
    scopes = ScopeFactory.create_batch(4)
    client = ClientFactory(scopes=scopes[:3])
    role = RoleFactory(scopes=scopes[1:])
    user = UserFactory(roles=(role,))
    calculated_user_access = get_user_access(user.id, client.id)
    required_user_access = UserAccess(scopes={
        scope.key: '*' for scope in scopes[1:3]
    })
    assert calculated_user_access == required_user_access


def test_provider_role():
    scopes = ScopeFactory.create_batch(4)
    client = ClientFactory(scopes=scopes[:3])
    role = RoleFactory(scopes=scopes[1:], is_provider_role=True)
    user = UserFactory(roles=(role,))
    calculated_user_access = get_user_access(user.id, client.id)
    required_scope_context = ScopeContext(
        projects='*',
        providers={role.provider.key},
        collections=set(),
    )
    required_user_access = UserAccess(scopes={
        scope.key: required_scope_context for scope in scopes[1:3]
    })
    assert calculated_user_access == required_user_access


def test_project_role():
    scopes = ScopeFactory.create_batch(4)
    client = ClientFactory(scopes=scopes[:3])
    role = RoleFactory(scopes=scopes[1:], is_project_role=True)
    user = UserFactory(roles=(role,))
    calculated_user_access = get_user_access(user.id, client.id)
    required_scope_context = ScopeContext(
        projects={role.project.key},
        providers='*',
        collections=set(),
    )
    required_user_access = UserAccess(scopes={
        scope.key: required_scope_context for scope in scopes[1:3]
    })
    assert calculated_user_access == required_user_access
