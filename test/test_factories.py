from sqlalchemy import select

from odp.api.models.auth import SystemScope
from odp.db import Session
from odp.db.models import (
    Client,
    Collection,
    Project,
    Provider,
    Role,
    RoleScope,
    Scope,
    User,
    UserRole,
)
from test.factories import (
    ClientFactory,
    CollectionFactory,
    ProjectFactory,
    ProviderFactory,
    RoleFactory,
    ScopeFactory,
    UserFactory,
)


def test_create_client():
    client = ClientFactory()
    result = Session.execute(select(Client))
    assert result.scalar_one().name == client.name


def test_create_collection():
    collection = CollectionFactory()
    result = Session.execute(select(Collection))
    assert result.scalar_one().key == collection.key


def test_create_project():
    project = ProjectFactory()
    result = Session.execute(select(Project))
    assert result.scalar_one().key == project.key


def test_create_provider():
    provider = ProviderFactory()
    result = Session.execute(select(Provider))
    assert result.scalar_one().key == provider.key


def test_create_role():
    role = RoleFactory()
    result = Session.execute(select(Role))
    assert result.scalar_one().key == role.key


def test_create_role_with_scopes():
    scopes = ScopeFactory.create_batch(2)
    role = RoleFactory(scopes=scopes)
    result = Session.execute(select(RoleScope.role_id, RoleScope.scope_id))
    assert result.all() == [(role.id, scope.id) for scope in scopes]


def test_create_role_with_system_scopes(static_data):
    system_scope_keys = [s.value for s in SystemScope]
    role = RoleFactory(system_scope_keys=system_scope_keys)
    result = Session.execute(select(Scope.key).join(RoleScope).where(RoleScope.role_id == role.id))
    assert result.scalars().all() == system_scope_keys


def test_create_scope():
    scope = ScopeFactory()
    result = Session.execute(select(Scope))
    assert result.scalar_one().key == scope.key


def test_create_user():
    user = UserFactory()
    result = Session.execute(select(User))
    assert result.scalar_one().email == user.email


def test_create_user_with_roles():
    roles = RoleFactory.create_batch(2)
    user = UserFactory(roles=roles)
    result = Session.execute(select(UserRole.user_id, UserRole.role_id))
    assert result.all() == [(user.id, role.id) for role in roles]
