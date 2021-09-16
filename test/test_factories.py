from sqlalchemy import select

from odp.db import Session
from odp.db.models import (
    Client,
    Collection,
    Project,
    Provider,
    Role,
    User,
    UserRole,
)
from test.factories import (
    ClientFactory,
    CollectionFactory,
    ProjectFactory,
    ProviderFactory,
    RoleFactory,
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


def test_create_user():
    user = UserFactory()
    result = Session.execute(select(User))
    assert result.scalar_one().email == user.email


def test_create_user_with_roles():
    roles = RoleFactory.create_batch(2)
    user = UserFactory(roles=roles, active=False)
    result = Session.execute(select(UserRole.user_id, UserRole.role_id))
    assert result.all() == [(user.id, role.id) for role in roles]
