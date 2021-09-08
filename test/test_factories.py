from sqlalchemy import select

from odp.db import Session
from odp.db.models import (
    Client,
    Project,
    Provider,
    Role,
    User,
)
from test.factories import (
    ClientFactory,
    ProjectFactory,
    ProviderFactory,
    RoleFactory,
    UserFactory,
)


def test_create_client():
    client = ClientFactory()
    result = Session.execute(select(Client))
    assert result.scalar_one().name == client.name


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
