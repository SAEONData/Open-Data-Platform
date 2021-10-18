from sqlalchemy import select

import migrate.initdb
from odp import ODPScope
from odp.db import Session
from odp.db.models import (
    Client,
    ClientScope,
    Collection,
    Project,
    ProjectCollection,
    Provider,
    Role,
    RoleScope,
    Scope,
    Tag,
    User,
    UserRole,
)
from test.factories import (
    ClientFactory,
    CollectionFactory,
    ProjectFactory,
    ProviderFactory,
    RoleFactory,
    ScopeFactory,
    TagFactory,
    UserFactory,
)


def test_db_setup():
    migrate.initdb.create_scopes(Session)
    Session.commit()
    result = Session.execute(select(Scope)).scalars()
    assert [row.id for row in result] == [s.value for s in ODPScope]

    ScopeFactory()  # create an arbitrary (external) scope, not for the sysadmin

    migrate.initdb.create_admin_role(Session)
    Session.commit()
    result = Session.execute(select(Role)).scalar_one()
    assert (result.id, result.provider_id) == (migrate.initdb.ODP_ADMIN_ROLE, None)

    result = Session.execute(select(RoleScope)).scalars()
    assert [(row.role_id, row.scope_id) for row in result] \
           == [(migrate.initdb.ODP_ADMIN_ROLE, s.value) for s in ODPScope]


def test_create_client():
    client = ClientFactory()
    result = Session.execute(select(Client)).scalar_one()
    assert (result.id, result.name, result.provider_id) == (client.id, client.name, None)


def test_create_client_with_provider():
    client = ClientFactory(is_provider_client=True)
    result = Session.execute(select(Client, Provider).join(Provider)).one()
    assert (result.Client.id, result.Client.name, result.Client.provider_id, result.Provider.name) \
           == (client.id, client.name, client.provider.id, client.provider.name)


def test_create_client_with_scopes():
    scopes = ScopeFactory.create_batch(5)
    client = ClientFactory(scopes=scopes)
    result = Session.execute(select(ClientScope)).scalars()
    assert [(row.client_id, row.scope_id) for row in result] \
           == [(client.id, scope.id) for scope in scopes]


def test_create_collection():
    collection = CollectionFactory()
    result = Session.execute(select(Collection, Provider).join(Provider)).one()
    assert (result.Collection.id, result.Collection.name, result.Collection.provider_id, result.Provider.name) \
           == (collection.id, collection.name, collection.provider.id, collection.provider.name)


def test_create_collection_with_projects():
    projects = ProjectFactory.create_batch(5)
    collection = CollectionFactory(projects=projects)
    result = Session.execute(select(ProjectCollection)).scalars()
    assert [(row.project_id, row.collection_id) for row in result] \
           == [(project.id, collection.id) for project in projects]


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
    scopes = ScopeFactory.create_batch(5)
    role = RoleFactory(scopes=scopes)
    result = Session.execute(select(RoleScope)).scalars()
    assert [(row.role_id, row.scope_id) for row in result] \
           == [(role.id, scope.id) for scope in scopes]


def test_create_scope():
    scope = ScopeFactory()
    result = Session.execute(select(Scope)).scalar_one()
    assert result.id == scope.id


def test_create_tag():
    tag = TagFactory()
    result = Session.execute(select(Tag, Scope).join(Scope)).one()
    assert (result.Tag.id, result.Tag.public, result.Tag.schema_uri, result.Tag.scope_id) \
           == (tag.id, tag.public, tag.schema_uri, tag.scope.id)


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
