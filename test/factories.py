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
    Scope,
    User,
    Tag,
)


def id_from_name(obj):
    return re.sub(r'[^a-z0-9]+', '-', obj.name.lower()).strip('-')


class ODPModelFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = 'commit'


class ClientFactory(ODPModelFactory):
    class Meta:
        model = Client

    id = factory.LazyAttribute(id_from_name)
    name = factory.Faker('catch_phrase')

    @factory.post_generation
    def scopes(obj, create, scopes):
        if not create:
            return
        if scopes:
            for scope in scopes:
                obj.scopes.append(scope)
            Session.commit()


class ProjectFactory(ODPModelFactory):
    class Meta:
        model = Project

    id = factory.LazyAttribute(id_from_name)
    name = factory.Faker('catch_phrase')


class ProviderFactory(ODPModelFactory):
    class Meta:
        model = Provider

    id = factory.LazyAttribute(id_from_name)
    name = factory.Faker('company')


class CollectionFactory(ODPModelFactory):
    class Meta:
        model = Collection

    id = factory.LazyAttribute(id_from_name)
    name = factory.Faker('catch_phrase')
    provider = factory.SubFactory(ProviderFactory)


class RoleFactory(ODPModelFactory):
    class Meta:
        model = Role
        exclude = ('is_project_role', 'is_provider_role')

    id = factory.LazyAttribute(id_from_name)
    name = factory.Faker('job')

    is_project_role = False
    is_provider_role = False

    project = factory.Maybe(
        'is_project_role',
        yes_declaration=factory.SubFactory(ProjectFactory),
        no_declaration=None,
    )
    provider = factory.Maybe(
        'is_provider_role',
        yes_declaration=factory.SubFactory(ProviderFactory),
        no_declaration=None,
    )

    @factory.post_generation
    def scopes(obj, create, scopes):
        if not create:
            return
        if scopes:
            for scope in scopes:
                obj.scopes.append(scope)
            Session.commit()


class ScopeFactory(ODPModelFactory):
    class Meta:
        model = Scope

    id = factory.Faker('word')


class UserFactory(ODPModelFactory):
    class Meta:
        model = User

    id = factory.Faker('uuid4')
    name = factory.Faker('name')
    email = factory.Faker('email')
    active = True
    verified = True

    @factory.post_generation
    def roles(obj, create, roles):
        if not create:
            return
        if roles:
            for role in roles:
                obj.roles.append(role)
            Session.commit()


class TagFactory(ODPModelFactory):
    class Meta:
        model = Tag

    id = factory.SelfAttribute('scope.id')
    public = True
    schema_uri = factory.Faker('uri')
    scope = factory.SubFactory(ScopeFactory)