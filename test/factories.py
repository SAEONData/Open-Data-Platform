import re

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from odp.db import Session
from odp.db.models import (
    Client,
    Collection,
    Project,
    Provider,
    Role,
    Scope,
    Tag,
    User,
)

fake = Faker()


def id_from_name(obj):
    return re.sub(r'[^a-z0-9]+', '-', obj.name.lower()).strip('-')


class ODPModelFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = 'commit'


class ProviderFactory(ODPModelFactory):
    class Meta:
        model = Provider

    id = factory.LazyAttribute(id_from_name)
    name = factory.Sequence(lambda n: f'{fake.company()}.{n}')


class ClientFactory(ODPModelFactory):
    class Meta:
        model = Client
        exclude = ('is_provider_client',)

    id = factory.LazyAttribute(id_from_name)
    name = factory.Sequence(lambda n: f'{fake.catch_phrase()}.{n}')

    is_provider_client = False
    provider = factory.Maybe(
        'is_provider_client',
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


class CollectionFactory(ODPModelFactory):
    class Meta:
        model = Collection

    id = factory.LazyAttribute(id_from_name)
    name = factory.Sequence(lambda n: f'{fake.catch_phrase()}.{n}')
    provider = factory.SubFactory(ProviderFactory)

    @factory.post_generation
    def projects(obj, create, projects):
        if not create:
            return
        if projects:
            for project in projects:
                obj.projects.append(project)
            Session.commit()


class ProjectFactory(ODPModelFactory):
    class Meta:
        model = Project

    id = factory.LazyAttribute(id_from_name)
    name = factory.Sequence(lambda n: f'{fake.catch_phrase()}.{n}')

    @factory.post_generation
    def collections(obj, create, collections):
        if collections:
            for collection in collections:
                obj.collections.append(collection)
            if create:
                Session.commit()


class RoleFactory(ODPModelFactory):
    class Meta:
        model = Role
        exclude = ('is_provider_role',)

    id = factory.Sequence(lambda n: f'{fake.job()}.{n}')

    is_provider_role = False
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

    id = factory.Sequence(lambda n: f'{fake.word()}.{n}')


class TagFactory(ODPModelFactory):
    class Meta:
        model = Tag

    id = factory.LazyAttribute(lambda tag: f'tag-{tag.scope.id}')
    public = True
    schema_uri = factory.Faker('uri')
    scope = factory.SubFactory(ScopeFactory)


class UserFactory(ODPModelFactory):
    class Meta:
        model = User

    id = factory.Faker('uuid4')
    name = factory.Faker('name')
    email = factory.Sequence(lambda n: f'{fake.email()}.{n}')
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
