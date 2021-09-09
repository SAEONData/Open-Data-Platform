import re

import factory
from factory.alchemy import SQLAlchemyModelFactory

from odp.db import Session
from odp.db.models import (
    Client,
    Collection,
    Project,
    Provider,
    Role,
    User,
)


def key_from_name(obj):
    return re.sub(r'[^a-z0-9]+', '-', obj.name.lower()).strip('-')


class ODPModelFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = 'commit'


class ClientFactory(ODPModelFactory):
    class Meta:
        model = Client

    id = factory.Faker('uuid4')
    name = factory.Faker('catch_phrase')


class ProjectFactory(ODPModelFactory):
    class Meta:
        model = Project

    id = factory.Sequence(int)
    key = factory.LazyAttribute(key_from_name)
    name = factory.Faker('catch_phrase')


class ProviderFactory(ODPModelFactory):
    class Meta:
        model = Provider

    id = factory.Sequence(int)
    key = factory.LazyAttribute(key_from_name)
    name = factory.Faker('company')


class CollectionFactory(ODPModelFactory):
    class Meta:
        model = Collection

    id = factory.Sequence(int)
    key = factory.LazyAttribute(key_from_name)
    name = factory.Faker('catch_phrase')
    provider = factory.SubFactory(ProviderFactory)


class RoleFactory(ODPModelFactory):
    class Meta:
        model = Role

    id = factory.Sequence(int)
    key = factory.LazyAttribute(key_from_name)
    name = factory.Faker('job')


class UserFactory(ODPModelFactory):
    class Meta:
        model = User

    id = factory.Faker('uuid4')
    email = factory.Faker('email')
    active = True
    verified = True
