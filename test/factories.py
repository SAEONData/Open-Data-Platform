import re

import factory
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import select

from odp.db import Session
from odp.db.models import (
    Client,
    Collection,
    Project,
    Provider,
    Role,
    Scope,
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

    @factory.post_generation
    def scopes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for scope in extracted:
                self.scopes.append(scope)
            Session.commit()

    @factory.post_generation
    def system_scopes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for system_scope in extracted:
                result = Session.execute(select(Scope).where(Scope.key == system_scope.value))
                scope = result.scalar_one()
                self.scopes.append(scope)
            Session.commit()


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

    @factory.post_generation
    def scopes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for scope in extracted:
                self.scopes.append(scope)
            Session.commit()

    @factory.post_generation
    def system_scopes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for system_scope in extracted:
                result = Session.execute(select(Scope).where(Scope.key == system_scope.value))
                scope = result.scalar_one()
                self.scopes.append(scope)
            Session.commit()


class ScopeFactory(ODPModelFactory):
    class Meta:
        model = Scope

    id = factory.Sequence(int)
    key = factory.Faker('word')


class UserFactory(ODPModelFactory):
    class Meta:
        model = User

    id = factory.Faker('uuid4')
    email = factory.Faker('email')
    active = True
    verified = True

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for role in extracted:
                self.roles.append(role)
            Session.commit()
