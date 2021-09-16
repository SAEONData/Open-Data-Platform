from odp.api.models.auth import SystemScope, UserAccess, ScopeContext
from odp.lib.auth import get_user_access
from test.factories import ClientFactory, RoleFactory, UserFactory


def test_unpinned_role(static_data):
    client = ClientFactory(system_scopes=(
        SystemScope.COLLECTION_VIEW,
        SystemScope.COLLECTION_MANAGE,
        SystemScope.DIGITALOBJECT_VIEW,
        SystemScope.DIGITALOBJECT_MANAGE,
    ))
    role = RoleFactory(system_scopes=(
        SystemScope.CATALOGUE_VIEW,
        SystemScope.COLLECTION_VIEW,
        SystemScope.DIGITALOBJECT_VIEW,
        SystemScope.PROJECT_VIEW,
    ))
    user = UserFactory(roles=(role,))
    calculated_user_access = get_user_access(user.id, client.id)
    required_user_access = UserAccess(scopes={
        SystemScope.COLLECTION_VIEW: '*',
        SystemScope.DIGITALOBJECT_VIEW: '*',
    })
    assert calculated_user_access == required_user_access


def test_provider_role(static_data):
    client = ClientFactory(system_scopes=(
        SystemScope.COLLECTION_VIEW,
        SystemScope.COLLECTION_MANAGE,
        SystemScope.DIGITALOBJECT_VIEW,
        SystemScope.DIGITALOBJECT_MANAGE,
    ))
    role = RoleFactory(is_provider_role=True, system_scopes=(
        SystemScope.CATALOGUE_VIEW,
        SystemScope.COLLECTION_VIEW,
        SystemScope.DIGITALOBJECT_VIEW,
        SystemScope.PROJECT_VIEW,
    ))
    user = UserFactory(roles=(role,))
    calculated_user_access = get_user_access(user.id, client.id)
    required_scope_context = ScopeContext(
        projects='*',
        providers={role.provider.key},
        collections=set(),
    )
    required_user_access = UserAccess(scopes={
        SystemScope.COLLECTION_VIEW: required_scope_context,
        SystemScope.DIGITALOBJECT_VIEW: required_scope_context,
    })
    assert calculated_user_access == required_user_access


def test_project_role(static_data):
    client = ClientFactory(system_scopes=(
        SystemScope.COLLECTION_VIEW,
        SystemScope.COLLECTION_MANAGE,
        SystemScope.DIGITALOBJECT_VIEW,
        SystemScope.DIGITALOBJECT_MANAGE,
    ))
    role = RoleFactory(is_project_role=True, system_scopes=(
        SystemScope.CATALOGUE_VIEW,
        SystemScope.COLLECTION_VIEW,
        SystemScope.DIGITALOBJECT_VIEW,
        SystemScope.PROJECT_VIEW,
    ))
    user = UserFactory(roles=(role,))
    calculated_user_access = get_user_access(user.id, client.id)
    required_scope_context = ScopeContext(
        projects={role.project.key},
        providers='*',
        collections=set(),
    )
    required_user_access = UserAccess(scopes={
        SystemScope.COLLECTION_VIEW: required_scope_context,
        SystemScope.DIGITALOBJECT_VIEW: required_scope_context,
    })
    assert calculated_user_access == required_user_access
