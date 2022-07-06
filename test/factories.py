import re
from datetime import datetime, timezone
from random import choice, randint

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from odp.db import Session
from odp.db.models import Catalog, Client, Collection, CollectionTag, Project, Provider, Record, RecordTag, Role, Schema, Scope, Tag, User

fake = Faker()


def id_from_name(obj):
    name, _, n = obj.name.rpartition('.')
    prefix, _, _ = name.partition(' ')
    return f'{_sanitize_id(prefix)}.{n}'


def id_from_fake(src, n):
    fake_val = getattr(fake, src)()
    return f'{_sanitize_id(fake_val)}.{n}'


def _sanitize_id(val):
    return re.sub(r'[^-.:\w]', '_', val)


def schema_uri_from_type(schema):
    if schema.type == 'metadata':
        return choice((
            'https://odp.saeon.ac.za/schema/metadata/saeon/datacite4',
            'https://odp.saeon.ac.za/schema/metadata/saeon/iso19115',
        ))
    elif schema.type == 'tag':
        return choice((
            'https://odp.saeon.ac.za/schema/tag/generic',
            'https://odp.saeon.ac.za/schema/tag/record/migrated',
            'https://odp.saeon.ac.za/schema/tag/record/qc',
            'https://odp.saeon.ac.za/schema/tag/record/embargo',
        ))
    elif schema.type == 'catalog':
        return choice((
            'https://odp.saeon.ac.za/schema/catalog/saeon',
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
    type = factory.LazyFunction(lambda: choice(('catalog', 'metadata', 'tag')))
    uri = factory.LazyAttribute(schema_uri_from_type)
    md5 = ''
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class CatalogFactory(ODPModelFactory):
    class Meta:
        model = Catalog

    id = factory.Sequence(lambda n: f'{fake.slug()}.{n}')
    schema = factory.SubFactory(SchemaFactory, type='catalog')


class ProviderFactory(ODPModelFactory):
    class Meta:
        model = Provider

    id = factory.LazyAttribute(id_from_name)
    name = factory.Sequence(lambda n: f'{fake.company()}.{n}')


class CollectionFactory(ODPModelFactory):
    class Meta:
        model = Collection

    id = factory.LazyAttribute(id_from_name)
    name = factory.Sequence(lambda n: f'{fake.catch_phrase()}.{n}')
    doi_key = factory.LazyFunction(lambda: fake.word() if randint(0, 1) else None)
    provider = factory.SubFactory(ProviderFactory)
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class ClientFactory(ODPModelFactory):
    class Meta:
        model = Client
        exclude = ('is_collection_client',)

    id = factory.Sequence(lambda n: id_from_fake('catch_phrase', n))

    is_collection_client = False
    collection = factory.Maybe(
        'is_collection_client',
        yes_declaration=factory.SubFactory(CollectionFactory),
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
    type = factory.LazyFunction(lambda: choice(('collection', 'record')))
    cardinality = factory.LazyFunction(lambda: choice(('one', 'user', 'multi')))
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


class CollectionTagFactory(ODPModelFactory):
    class Meta:
        model = CollectionTag

    collection = factory.SubFactory(CollectionFactory)
    tag = factory.SubFactory(TagFactory, type='collection')
    user = factory.SubFactory(UserFactory)
    data = {}
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))


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
        exclude = ('identifiers',)

    identifiers = factory.LazyFunction(lambda: choice(('doi', 'sid', 'both')))
    doi = factory.LazyAttributeSequence(lambda r, n: f'10.5555/test-{n}' if r.identifiers in ('doi', 'both') else None)
    sid = factory.LazyAttributeSequence(lambda r, n: f'test-{n}' if r.doi is None or r.identifiers in ('sid', 'both') else None)
    metadata_ = factory.LazyAttribute(lambda r: {'doi': r.doi} if r.doi else {})
    validity = {}
    collection = factory.SubFactory(CollectionFactory)
    schema = factory.SubFactory(SchemaFactory, type='metadata')
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class RecordTagFactory(ODPModelFactory):
    class Meta:
        model = RecordTag

    record = factory.SubFactory(RecordFactory)
    tag = factory.SubFactory(TagFactory, type='record')
    user = factory.SubFactory(UserFactory)
    data = {}
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class RoleFactory(ODPModelFactory):
    class Meta:
        model = Role
        exclude = ('is_collection_role',)

    id = factory.Sequence(lambda n: id_from_fake('job', n))

    is_collection_role = False
    collection = factory.Maybe(
        'is_collection_role',
        yes_declaration=factory.SubFactory(CollectionFactory),
        no_declaration=None,
    )

    @factory.post_generation
    def scopes(obj, create, scopes):
        if scopes:
            for scope in scopes:
                obj.scopes.append(scope)
            if create:
                Session.commit()
