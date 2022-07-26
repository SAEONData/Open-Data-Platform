from sqlalchemy import select

import migrate.systemdata
from odp import ODPScope
from odp.db import Session
from odp.db.models import (Catalog, Client, ClientScope, Collection, CollectionTag, Provider, Record, RecordTag, Role,
                           RoleScope, Schema, Scope, ScopeType, Tag, User, UserRole, Vocabulary, VocabularyTerm)
from test.factories import (CatalogFactory, ClientFactory, CollectionFactory, CollectionTagFactory, ProviderFactory, RecordFactory,
                            RecordTagFactory, RoleFactory, SchemaFactory, ScopeFactory, TagFactory, UserFactory, VocabularyFactory)


def test_db_setup():
    migrate.systemdata.init_system_scopes()
    Session.commit()
    result = Session.execute(select(Scope)).scalars()
    assert [row.id for row in result] == [s.value for s in ODPScope]

    # create a batch of arbitrary scopes, which should not be assigned to the sysadmin
    ScopeFactory.create_batch(5)

    migrate.systemdata.init_admin_role()
    Session.commit()
    result = Session.execute(select(Role)).scalar_one()
    assert (result.id, result.collection_id) == (migrate.systemdata.ODP_ADMIN_ROLE, None)

    result = Session.execute(select(RoleScope)).scalars()
    assert [(row.role_id, row.scope_id, row.scope_type) for row in result] \
           == [(migrate.systemdata.ODP_ADMIN_ROLE, s.value, ScopeType.odp) for s in ODPScope]


def test_create_catalog():
    catalog = CatalogFactory()
    result = Session.execute(select(Catalog)).scalar_one()
    assert result.id == catalog.id


def test_create_client():
    client = ClientFactory()
    result = Session.execute(select(Client)).scalar_one()
    assert (result.id, result.collection_id) == (client.id, None)


def test_create_client_with_collection():
    client = ClientFactory(is_collection_client=True)
    result = Session.execute(select(Client, Collection).join(Collection)).one()
    assert (result.Client.id, result.Client.collection_id, result.Collection.name) \
           == (client.id, client.collection.id, client.collection.name)


def test_create_client_with_scopes():
    scopes = ScopeFactory.create_batch(5)
    client = ClientFactory(scopes=scopes)
    result = Session.execute(select(ClientScope)).scalars()
    assert [(row.client_id, row.scope_id, row.scope_type) for row in result] \
           == [(client.id, scope.id, scope.type) for scope in scopes]


def test_create_collection():
    collection = CollectionFactory()
    result = Session.execute(select(Collection, Provider).join(Provider)).one()
    assert (result.Collection.id, result.Collection.name, result.Collection.doi_key, result.Collection.provider_id, result.Provider.name) \
           == (collection.id, collection.name, collection.doi_key, collection.provider.id, collection.provider.name)


def test_create_collection_tag():
    collection_tag = CollectionTagFactory()
    result = Session.execute(select(CollectionTag).join(Collection).join(Tag)).scalar_one()
    assert (result.collection_id, result.tag_id, result.tag_type, result.user_id, result.data) \
           == (collection_tag.collection.id, collection_tag.tag.id, 'collection', collection_tag.user.id, collection_tag.data)


def test_create_provider():
    provider = ProviderFactory()
    result = Session.execute(select(Provider)).scalar_one()
    assert (result.id, result.name) == (provider.id, provider.name)


def test_create_record():
    record = RecordFactory()
    result = Session.execute(select(Record)).scalar_one()
    assert (result.id, result.doi, result.sid, result.metadata_, result.validity, result.collection_id, result.schema_id, result.schema_type) \
           == (record.id, record.doi, record.sid, record.metadata_, record.validity, record.collection.id, record.schema.id, record.schema.type)


def test_create_record_tag():
    record_tag = RecordTagFactory()
    result = Session.execute(select(RecordTag).join(Record).join(Tag)).scalar_one()
    assert (result.record_id, result.tag_id, result.tag_type, result.user_id, result.data) \
           == (record_tag.record.id, record_tag.tag.id, 'record', record_tag.user.id, record_tag.data)


def test_create_role():
    role = RoleFactory()
    result = Session.execute(select(Role)).scalar_one()
    assert (result.id, result.collection_id) == (role.id, None)


def test_create_role_with_collection():
    role = RoleFactory(is_collection_role=True)
    result = Session.execute(select(Role, Collection).join(Collection)).one()
    assert (result.Role.id, result.Role.collection_id, result.Collection.name) \
           == (role.id, role.collection.id, role.collection.name)


def test_create_role_with_scopes():
    scopes = ScopeFactory.create_batch(5, type='odp') + ScopeFactory.create_batch(5, type='client')
    role = RoleFactory(scopes=scopes)
    result = Session.execute(select(RoleScope)).scalars()
    assert [(row.role_id, row.scope_id, row.scope_type) for row in result] \
           == [(role.id, scope.id, scope.type) for scope in scopes]


def test_create_schema():
    schema = SchemaFactory()
    result = Session.execute(select(Schema)).scalar_one()
    assert (result.id, result.type, result.uri) == (schema.id, schema.type, schema.uri)


def test_create_scope():
    scope = ScopeFactory()
    result = Session.execute(select(Scope)).scalar_one()
    assert (result.id, result.type) == (scope.id, scope.type)


def test_create_tag():
    tag = TagFactory()
    result = Session.execute(select(Tag, Scope).join(Scope)).one()
    assert (result.Tag.id, result.Tag.type, result.Tag.cardinality, result.Tag.public, result.Tag.schema_id, result.Tag.scope_id,
            result.Tag.scope_type) \
           == (tag.id, tag.type, tag.cardinality, tag.public, tag.schema_id, tag.scope.id, ScopeType.odp)


def test_create_user():
    user = UserFactory()
    result = Session.execute(select(User)).scalar_one()
    assert (result.id, result.name, result.email, result.active, result.verified) \
           == (user.id, user.name, user.email, user.active, user.verified)


def test_create_user_with_roles():
    roles = RoleFactory.create_batch(5)
    user = UserFactory(roles=roles)
    result = Session.execute(select(UserRole)).scalars()
    assert [(row.user_id, row.role_id) for row in result] \
           == [(user.id, role.id) for role in roles]


def test_create_vocabulary():
    vocabulary = VocabularyFactory()
    result = Session.execute(select(Vocabulary, VocabularyTerm).join(VocabularyTerm))
    assert [(
        row.Vocabulary.id,
        row.Vocabulary.scope_id,
        row.Vocabulary.scope_type,
        row.Vocabulary.schema_id,
        row.Vocabulary.schema_type,
        row.VocabularyTerm.vocabulary_id,
        row.VocabularyTerm.term_id,
        row.VocabularyTerm.data
    ) for row in result] == [(
        vocabulary.id,
        vocabulary.scope_id,
        'odp',
        vocabulary.schema_id,
        'vocabulary',
        term.vocabulary_id,
        term.term_id,
        term.data,
    ) for term in vocabulary.terms]
