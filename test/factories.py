from datetime import datetime, timezone
from random import randint, choice

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from odp.db import Session
from odp.db.models import (
    Catalogue,
    Client,
    Collection,
    Flag,
    Project,
    Provider,
    Record,
    Role,
    Schema,
    Scope,
    Tag,
    User,
)

fake = Faker()


def id_from_name(obj):
    name, _, n = obj.name.rpartition('.')
    prefix, _, _ = name.partition(' ')
    return f'{prefix}.{n}'


def schema_uri_from_type(schema):
    if schema.type == 'metadata':
        return choice((
            'https://odp.saeon.ac.za/schema/metadata/datacite4-saeon',
            'https://odp.saeon.ac.za/schema/metadata/iso19115-saeon',
        ))
    elif schema.type == 'flag':
        return choice((
            'https://odp.saeon.ac.za/schema/flag/generic',
        ))
    elif schema.type == 'tag':
        return choice((
            'https://odp.saeon.ac.za/schema/tag/record-qc',
        ))
    elif schema.type == 'catalogue':
        return choice((
            'https://odp.saeon.ac.za/schema/catalogue/saeon-catalogue',
        ))
    else:
        return fake.uri()


class ODPModelFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = 'commit'


class ScopeFactory(ODPModelFactory):
    class Meta:
        model = Scope

    id = factory.Sequence(lambda n: f'{fake.word()}.{n}')
    type = factory.LazyFunction(lambda: choice(('odp', 'oauth', 'client')))


class SchemaFactory(ODPModelFactory):
    class Meta:
        model = Schema

    id = factory.Sequence(lambda n: f'{fake.word()}.{n}')
    type = factory.LazyFunction(lambda: choice(('catalogue', 'metadata', 'flag', 'tag')))
    uri = factory.LazyAttribute(schema_uri_from_type)


class CatalogueFactory(ODPModelFactory):
    class Meta:
        model = Catalogue

    id = factory.Sequence(lambda n: f'{fake.slug()}.{n}')
    schema = factory.SubFactory(SchemaFactory, type='catalogue')


class ProviderFactory(ODPModelFactory):
    class Meta:
        model = Provider

    id = factory.LazyAttribute(id_from_name)
    name = factory.Sequence(lambda n: f'{fake.company()}.{n}')


class ClientFactory(ODPModelFactory):
    class Meta:
        model = Client
        exclude = ('is_provider_client',)

    id = factory.Sequence(lambda n: f'{fake.catch_phrase().replace("/", "|")}.{n}')

    is_provider_client = False
    provider = factory.Maybe(
        'is_provider_client',
        yes_declaration=factory.SubFactory(ProviderFactory),
        no_declaration=None,
    )

    @factory.post_generation
    def scopes(obj, create, scopes):
        if scopes:
            for scope in scopes:
                obj.scopes.append(scope)
            if create:
                Session.commit()


class CollectionFactory(ODPModelFactory):
    class Meta:
        model = Collection

    id = factory.LazyAttribute(id_from_name)
    name = factory.Sequence(lambda n: f'{fake.catch_phrase()}.{n}')
    doi_key = factory.LazyFunction(lambda: fake.word() if randint(0, 1) else None)
    provider = factory.SubFactory(ProviderFactory)

    @factory.post_generation
    def projects(obj, create, projects):
        if projects:
            for project in projects:
                obj.projects.append(project)
            if create:
                Session.commit()


class FlagFactory(ODPModelFactory):
    class Meta:
        model = Flag

    id = factory.LazyAttribute(lambda flag: f'flag-{flag.scope.id}')
    public = factory.LazyFunction(lambda: randint(0, 1))
    scope = factory.SubFactory(ScopeFactory, type='odp')
    schema = factory.SubFactory(SchemaFactory, type='flag')


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


class RecordFactory(ODPModelFactory):
    class Meta:
        model = Record

    doi = factory.Sequence(lambda n: f'10.5555/test-{n}')
    sid = factory.Sequence(lambda n: f'test-{n}' if randint(0, 1) else None)
    metadata_ = factory.LazyAttribute(lambda record: {'doi': record.doi})
    validity = {}
    collection = factory.SubFactory(CollectionFactory)
    schema = factory.SubFactory(SchemaFactory, type='metadata')
    timestamp = datetime.now(timezone.utc)


class RoleFactory(ODPModelFactory):
    class Meta:
        model = Role
        exclude = ('is_provider_role',)

    id = factory.Sequence(lambda n: f'{fake.job().replace("/", "|")}.{n}')

    is_provider_role = False
    provider = factory.Maybe(
        'is_provider_role',
        yes_declaration=factory.SubFactory(ProviderFactory),
        no_declaration=None,
    )

    @factory.post_generation
    def scopes(obj, create, scopes):
        if scopes:
            for scope in scopes:
                obj.scopes.append(scope)
            if create:
                Session.commit()


class TagFactory(ODPModelFactory):
    class Meta:
        model = Tag

    id = factory.LazyAttribute(lambda tag: f'tag-{tag.scope.id}')
    public = factory.LazyFunction(lambda: randint(0, 1))
    scope = factory.SubFactory(ScopeFactory, type='odp')
    schema = factory.SubFactory(SchemaFactory, type='tag')


class UserFactory(ODPModelFactory):
    class Meta:
        model = User

    id = factory.Faker('uuid4')
    name = factory.Faker('name')
    email = factory.Sequence(lambda n: f'{fake.email()}.{n}')
    active = factory.LazyFunction(lambda: randint(0, 1))
    verified = factory.LazyFunction(lambda: randint(0, 1))

    @factory.post_generation
    def roles(obj, create, roles):
        if roles:
            for role in roles:
                obj.roles.append(role)
            if create:
                Session.commit()
