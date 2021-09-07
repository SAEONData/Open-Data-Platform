import pytest
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from odp.db import session, transaction
from odp.db.models import Client, Role, User
from test.factories import ClientFactory, RoleFactory, UserFactory


def test_create_client():
    with transaction():
        client = ClientFactory()
        name = client.name
    result = session.execute(select(Client))
    assert result.scalar_one().name == name


def test_create_client_uncommitted():
    ClientFactory()
    with pytest.raises(NoResultFound):
        session.execute(select(Client)).one()


def test_create_role():
    with transaction():
        role = RoleFactory()
        key = role.key
    result = session.execute(select(Role))
    assert result.scalar_one().key == key


def test_create_role_uncommitted():
    RoleFactory()
    with pytest.raises(NoResultFound):
        session.execute(select(Role)).one()


def test_create_user():
    with transaction():
        user = UserFactory()
        email = user.email
    result = session.execute(select(User))
    assert result.scalar_one().email == email


def test_create_user_uncommitted():
    UserFactory()
    with pytest.raises(NoResultFound):
        session.execute(select(User)).one()
