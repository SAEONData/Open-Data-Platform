#!/usr/bin/env python
"""
This script creates the ODP database schema and initializes
static system data. It should be run from the ../deploy or
../develop directory, as applicable.

An admin user is created, with prompts, if not found.

The script may be re-run as needed to synchronize static
data with the ODP codebase.
"""

import os
import pathlib
import sys
from getpass import getpass

import argon2
import yaml
from dotenv import load_dotenv
from sqlalchemy import delete, select

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

dotenv_path = pathlib.Path.cwd() / '.env'
load_dotenv(dotenv_path)

from odp import ODPScope
from odp.db import Base, Session, engine
from odp.db.models import Catalog, Client, Flag, Role, Schema, SchemaType, Scope, ScopeType, Tag, User, UserRole
from odp.lib.hydra import GrantType, HydraAdminAPI, HydraScope, ResponseType

datadir = pathlib.Path(__file__).parent / 'systemdata'

ODP_ADMIN_ROLE = 'ODP:Admin'


def create_db_schema():
    """Create the ODP database schema.

    Only tables that do not exist are created. To modify existing table
    definitions, use Alembic migrations.
    """
    Base.metadata.create_all(engine)


def init_system_scopes():
    """Create or update the set of available ODP system scopes."""
    for scope_id in (scope_ids := [s.value for s in ODPScope]):
        if not Session.get(Scope, (scope_id, ScopeType.odp)):
            scope = Scope(id=scope_id, type=ScopeType.odp)
            scope.save()

    Session.execute(
        delete(Scope).
        where(Scope.type == ScopeType.odp).
        where(Scope.id.not_in(scope_ids))
    )


def init_standard_scopes():
    """Create or update the set of available standard OAuth2 scopes."""
    for scope_id in (scope_ids := [s.value for s in HydraScope]):
        if not Session.get(Scope, (scope_id, ScopeType.oauth)):
            scope = Scope(id=scope_id, type=ScopeType.oauth)
            scope.save()

    Session.execute(
        delete(Scope).
        where(Scope.type == ScopeType.oauth).
        where(Scope.id.not_in(scope_ids))
    )


def init_admin_role():
    """Create the ODP admin role if it does not exist, and
    synchronize its scopes with the system."""
    role = Session.get(Role, ODP_ADMIN_ROLE) or Role(id=ODP_ADMIN_ROLE)
    role.scopes = [Session.get(Scope, (s.value, ScopeType.odp)) for s in ODPScope]
    role.save()


def init_admin_client():
    """Create or update the ODP Admin UI client."""
    client = Session.get(Client, ODP_UI_ADMIN_CLIENT_ID) or Client(id=ODP_UI_ADMIN_CLIENT_ID)
    client.scopes = [Session.get(Scope, (s.value, ScopeType.odp)) for s in ODPScope] + \
                    [Session.get(Scope, (HydraScope.OPENID, ScopeType.oauth))] + \
                    [Session.get(Scope, (HydraScope.OFFLINE_ACCESS, ScopeType.oauth))]
    client.save()

    hydra_admin_api.create_or_update_client(
        id=ODP_UI_ADMIN_CLIENT_ID,
        name=ODP_UI_ADMIN_CLIENT_NAME,
        secret=ODP_UI_ADMIN_CLIENT_SECRET,
        scope_ids=[s.value for s in ODPScope] + [HydraScope.OPENID, HydraScope.OFFLINE_ACCESS],
        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
        response_types=[ResponseType.CODE],
        redirect_uris=[ODP_UI_ADMIN_LOGGED_IN_URL],
        post_logout_redirect_uris=[ODP_UI_ADMIN_LOGGED_OUT_URL],
    )


def init_dap_client():
    """Create or update the Data Access Portal client."""
    client = Session.get(Client, ODP_UI_DAP_CLIENT_ID) or Client(id=ODP_UI_DAP_CLIENT_ID)
    client.scopes = [Session.get(Scope, (HydraScope.OPENID, ScopeType.oauth))] + \
                    [Session.get(Scope, (HydraScope.OFFLINE_ACCESS, ScopeType.oauth))]
    client.save()

    hydra_admin_api.create_or_update_client(
        id=ODP_UI_DAP_CLIENT_ID,
        name=ODP_UI_DAP_CLIENT_NAME,
        secret=ODP_UI_DAP_CLIENT_SECRET,
        scope_ids=[HydraScope.OPENID, HydraScope.OFFLINE_ACCESS],
        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
        response_types=[ResponseType.CODE],
        redirect_uris=[ODP_UI_DAP_LOGGED_IN_URL],
        post_logout_redirect_uris=[ODP_UI_DAP_LOGGED_OUT_URL],
    )


def init_cli_client():
    """Create or update the Swagger UI client."""
    client = Session.get(Client, ODP_CLI_CLIENT_ID) or Client(id=ODP_CLI_CLIENT_ID)
    client.scopes = [Session.get(Scope, (s.value, ScopeType.odp)) for s in ODPScope]
    client.save()

    hydra_admin_api.create_or_update_client(
        id=ODP_CLI_CLIENT_ID,
        name=ODP_CLI_CLIENT_NAME,
        secret=ODP_CLI_CLIENT_SECRET,
        scope_ids=[s.value for s in ODPScope],
        grant_types=[GrantType.CLIENT_CREDENTIALS],
    )


def init_admin_user():
    """Create an admin user if one is not found."""
    if not Session.execute(
            select(UserRole).where(UserRole.role_id == ODP_ADMIN_ROLE)
    ).first():
        print('Creating an admin user...')
        while not (name := input('Full name: ')):
            pass
        while not (email := input('Email: ')):
            pass
        while not (password := getpass()):
            pass

        user = User(
            name=name,
            email=email,
            password=argon2.PasswordHasher().hash(password),
            active=True,
            verified=True,
        )
        user.save()

        user_role = UserRole(
            user_id=user.id,
            role_id=ODP_ADMIN_ROLE,
        )
        user_role.save()


def init_schemas():
    """Create or update schema definitions."""
    with open(datadir / 'schemas.yml') as f:
        schema_data = yaml.safe_load(f)

    for schema_id, schema_spec in schema_data.items():
        schema_type = schema_spec['type']
        schema = Session.get(Schema, (schema_id, schema_type)) or Schema(id=schema_id, type=schema_type)
        schema.uri = schema_spec['uri']
        schema.save()


def init_flags():
    """Create or update flag definitions."""
    with open(datadir / 'flags.yml') as f:
        flag_data = yaml.safe_load(f)

    for flag_id, flag_spec in flag_data.items():
        flag_type = flag_spec['type']
        flag = Session.get(Flag, (flag_id, flag_type)) or Flag(id=flag_id, type=flag_type)
        flag.public = flag_spec['public']
        flag.scope_id = flag_spec['scope_id']
        flag.scope_type = ScopeType.odp
        flag.schema_id = flag_spec['schema_id']
        flag.schema_type = SchemaType.flag
        flag.save()


def init_tags():
    """Create or update tag definitions."""
    with open(datadir / 'tags.yml') as f:
        tag_data = yaml.safe_load(f)

    for tag_id, tag_spec in tag_data.items():
        tag_type = tag_spec['type']
        tag = Session.get(Tag, (tag_id, tag_type)) or Tag(id=tag_id, type=tag_type)
        tag.public = tag_spec['public']
        tag.scope_id = tag_spec['scope_id']
        tag.scope_type = ScopeType.odp
        tag.schema_id = tag_spec['schema_id']
        tag.schema_type = SchemaType.tag
        tag.save()


def init_roles():
    """Create or update role definitions."""
    with open(datadir / 'roles.yml') as f:
        role_data = yaml.safe_load(f)

    for role_id, role_spec in role_data.items():
        role = Session.get(Role, role_id) or Role(id=role_id)
        role.scopes = [Session.get(Scope, (scope_id, ScopeType.odp)) for scope_id in role_spec['scopes']]
        role.save()


def init_catalogs():
    """Create or update catalog definitions."""
    with open(datadir / 'catalogs.yml') as f:
        catalog_data = yaml.safe_load(f)

    for catalog_id, catalog_spec in catalog_data.items():
        catalog = Session.get(Catalog, catalog_id) or Catalog(id=catalog_id)
        catalog.schema_id = catalog_spec['schema_id']
        catalog.schema_type = SchemaType.catalog
        catalog.save()


if __name__ == '__main__':
    print('Initializing static system data...')

    ODP_UI_ADMIN_CLIENT_ID = os.getenv('ODP_UI_ADMIN_CLIENT_ID')
    ODP_UI_ADMIN_CLIENT_SECRET = os.getenv('ODP_UI_ADMIN_CLIENT_SECRET')
    ODP_UI_ADMIN_CLIENT_NAME = 'ODP Admin UI'
    ODP_UI_ADMIN_LOGGED_IN_URL = os.getenv('ODP_UI_ADMIN_URL') + '/oauth2/logged_in'
    ODP_UI_ADMIN_LOGGED_OUT_URL = os.getenv('ODP_UI_ADMIN_URL') + '/oauth2/logged_out'

    ODP_UI_DAP_CLIENT_ID = os.getenv('ODP_UI_DAP_CLIENT_ID')
    ODP_UI_DAP_CLIENT_SECRET = os.getenv('ODP_UI_DAP_CLIENT_SECRET')
    ODP_UI_DAP_CLIENT_NAME = 'ODP Data Access Portal'
    ODP_UI_DAP_LOGGED_IN_URL = os.getenv('ODP_UI_DAP_URL') + '/oauth2/logged_in'
    ODP_UI_DAP_LOGGED_OUT_URL = os.getenv('ODP_UI_DAP_URL') + '/oauth2/logged_out'

    ODP_CLI_CLIENT_ID = os.getenv('ODP_CLI_CLIENT_ID')
    ODP_CLI_CLIENT_SECRET = os.getenv('ODP_CLI_CLIENT_SECRET')
    ODP_CLI_CLIENT_NAME = 'Swagger UI / Scripting Client'

    hydra_admin_api = HydraAdminAPI(os.getenv('HYDRA_ADMIN_URL'))

    create_db_schema()
    with Session.begin():
        init_system_scopes()
        init_standard_scopes()
        init_admin_role()
        init_admin_client()
        init_dap_client()
        init_cli_client()
        init_admin_user()
        init_schemas()
        init_flags()
        init_tags()
        init_roles()
        init_catalogs()

    print('Done.')
