from sqlalchemy import select

import migrate.systemdata
from odp import ODPScope
from odp.db import Session
from odp.db.models import (
    Catalogue,
    Client,
    ClientScope,
    Collection,
    Flag,
    Project,
    ProjectCollection,
    Provider,
    Record,
    Role,
    RoleScope,
    Schema,
    Scope,
    Tag,
    User,
    UserRole,
)
from test.factories import (
    CatalogueFactory,
    ClientFactory,
    CollectionFactory,
    FlagFactory,
    ProjectFactory,
    ProviderFactory,
    RecordFactory,
    RoleFactory,
    SchemaFactory,
    ScopeFactory,
    TagFactory,
    UserFactory,
)


def test_db_setup():
    migrate.systemdata.sync_system_scopes()
    Session.commit()
    result = Session.execute(select(Scope)).scalars()
    assert [row.id for row in result] == [s.value for s in ODPScope]

    ScopeFactory()  # create an arbitrary (external) scope, not for the sysadmin

    migrate.systemdata.sync_admin_role()
    Session.commit()
    result = Session.execute(select(Role)).scalar_one()
    assert (result.id, result.provider_id) == (migrate.systemdata.ODP_ADMIN_ROLE, None)

    result = Session.execute(select(RoleScope)).scalars()
    assert [(row.role_id, row.scope_id) for row in result] \
           == [(migrate.systemdata.ODP_ADMIN_ROLE, s.value) for s in ODPScope]


def test_create_catalogue():
    catalogue = CatalogueFactory()
    result = Session.execute(select(Catalogue, Schema).join(Schema)).one()
    assert (result.Catalogue.id, result.Catalogue.schema_id, result.Catalogue.schema_type, result.Schema.uri) \
           == (catalogue.id, catalogue.schema_id, catalogue.schema_type, catalogue.schema.uri)


def test_create_client():
    client = ClientFactory()
    result = Session.execute(select(Client)).scalar_one()
    assert (result.id, result.provider_id) == (client.id, None)


def test_create_client_with_provider():
    client = ClientFactory(is_provider_client=True)
    result = Session.execute(select(Client, Provider).join(Provider)).one()
    assert (result.Client.id, result.Client.provider_id, result.Provider.name) \
           == (client.id, client.provider.id, client.provider.name)


def test_create_client_with_scopes():
    scopes = ScopeFactory.create_batch(5)
    client = ClientFactory(scopes=scopes)
    result = Session.execute(select(ClientScope)).scalars()
    assert [(row.client_id, row.scope_id) for row in result] \
           == [(client.id, scope.id) for scope in scopes]


def test_create_collection():
    collection = CollectionFactory()
    result = Session.execute(select(Collection, Provider).join(Provider)).one()
    assert (result.Collection.id, result.Collection.name, result.Collection.doi_key, result.Collection.provider_id, result.Provider.name) \
           == (collection.id, collection.name, collection.doi_key, collection.provider.id, collection.provider.name)


def test_create_flag():
    flag = FlagFactory()
    result = Session.execute(select(Flag, Scope).join(Scope)).one()
    assert (result.Flag.id, result.Flag.public, result.Flag.schema_id, result.Flag.scope_id) \
           == (flag.id, flag.public, flag.schema_id, flag.scope.id)


def test_create_project():
    project = ProjectFactory()
    result = Session.execute(select(Project)).scalar_one()
    assert (result.id, result.name) == (project.id, project.name)


def test_create_project_with_collections():
    collections = CollectionFactory.create_batch(5)
    project = ProjectFactory(collections=collections)
    result = Session.execute(select(ProjectCollection)).scalars()
    assert [(row.project_id, row.collection_id) for row in result] \
           == [(project.id, collection.id) for collection in collections]


def test_create_provider():
    provider = ProviderFactory()
    result = Session.execute(select(Provider)).scalar_one()
    assert (result.id, result.name) == (provider.id, provider.name)


def test_create_record():
    record = RecordFactory()
    result = Session.execute(select(Record)).scalar_one()
    assert (result.id, result.doi, result.sid, result.metadata_, result.validity, result.collection_id, result.schema_id, result.schema_type) \
           == (record.id, record.doi, record.sid, record.metadata_, record.validity, record.collection.id, record.schema.id, record.schema.type)


def test_create_role():
    role = RoleFactory()
    result = Session.execute(select(Role)).scalar_one()
    assert (result.id, result.provider_id) == (role.id, None)


def test_create_role_with_provider():
    role = RoleFactory(is_provider_role=True)
    result = Session.execute(select(Role, Provider).join(Provider)).one()
    assert (result.Role.id, result.Role.provider_id, result.Provider.name) \
           == (role.id, role.provider.id, role.provider.name)


def test_create_role_with_scopes():
    scopes = ScopeFactory.create_batch(5, type='odp')
    role = RoleFactory(scopes=scopes)
    result = Session.execute(select(RoleScope)).scalars()
    assert [(row.role_id, row.scope_id) for row in result] \
           == [(role.id, scope.id) for scope in scopes]


def test_create_schema():
    schema = SchemaFactory()
    result = Session.execute(select(Schema)).scalar_one()
    assert (result.id, result.type, result.uri) == (schema.id, schema.type, schema.uri)


def test_create_scope():
    scope = ScopeFactory()
    result = Session.execute(select(Scope)).scalar_one()
    assert result.id == scope.id


def test_create_tag():
    tag = TagFactory()
    result = Session.execute(select(Tag, Scope).join(Scope)).one()
    assert (result.Tag.id, result.Tag.public, result.Tag.schema_id, result.Tag.scope_id) \
           == (tag.id, tag.public, tag.schema_id, tag.scope.id)


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
