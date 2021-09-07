import re
import uuid

import factory
from factory.alchemy import SQLAlchemyModelFactory

from odp.db import session
from odp.db.models import Client, Role, User


def keyify(name: str):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = session

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker('sentence', nb_words=3)

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        kwargs['name'] = kwargs['name'].title().rstrip('.')
        return kwargs


class RoleFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Role
        sqlalchemy_session = session

    id = factory.Sequence(int)
    key = factory.LazyAttribute(lambda r: keyify(r.name))
    name = factory.Faker('job')


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = session

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Faker('email')
    active = True
    verified = True
