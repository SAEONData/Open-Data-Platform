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
from dotenv import load_dotenv
from sqlalchemy import delete, select

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

dotenv_path = pathlib.Path.cwd() / '.env'
load_dotenv(dotenv_path)

from odp import ODPScope
from odp.db import engine, Session, Base
from odp.db.models import Scope, Role, Client, User, UserRole
from odp.lib.hydra import HydraAdminAPI, GrantType, HydraScope, ResponseType

ODP_ADMIN_ROLE = 'ODP:Admin'

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

HYDRA_ADMIN_URL = os.getenv('HYDRA_ADMIN_URL')

hydra_admin_api = HydraAdminAPI(HYDRA_ADMIN_URL)


def create_schema():
    """Create the ODP database schema.

    Only tables that do not exist are created. To modify existing table
    definitions, use Alembic migrations.
    """
    Base.metadata.create_all(engine)


def sync_system_scopes():
    """Create any ODP system scopes that do not exist, and
    delete any that are obsolete."""
    for scope_id in (scope_ids := [s.value for s in ODPScope]):
        if not Session.get(Scope, scope_id):
            scope = Scope(id=scope_id)
            scope.save()

    Session.execute(
        delete(Scope).
        where(Scope.id.like('odp.%')).
        where(Scope.id.not_in(scope_ids)).
        execution_options(synchronize_session=False)
    )


def sync_admin_role():
    """Create the ODP admin role if it does not exist, and
    synchronize its scopes with the system."""
    role = Session.get(Role, ODP_ADMIN_ROLE) or Role(id=ODP_ADMIN_ROLE)
    role.scopes = [Session.get(Scope, s.value) for s in ODPScope]
    role.save()


def sync_admin_client():
    """Create or update the ODP Admin UI client."""
    client = Session.get(Client, ODP_UI_ADMIN_CLIENT_ID) or Client(id=ODP_UI_ADMIN_CLIENT_ID)
    client.name = ODP_UI_ADMIN_CLIENT_NAME,
    client.scopes = [Session.get(Scope, s.value) for s in ODPScope]
    client.save()

    hydra_admin_api.create_or_update_client(
        id=ODP_UI_ADMIN_CLIENT_ID,
        name=ODP_UI_ADMIN_CLIENT_NAME,
        secret=ODP_UI_ADMIN_CLIENT_SECRET,
        scope_ids=[HydraScope.OPENID, HydraScope.OFFLINE_ACCESS] + [s.value for s in ODPScope],
        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
        response_types=[ResponseType.CODE],
        redirect_uris=[ODP_UI_ADMIN_LOGGED_IN_URL],
        post_logout_redirect_uris=[ODP_UI_ADMIN_LOGGED_OUT_URL],
    )


def sync_dap_client():
    """Create or update the Data Access Portal client."""
    client = Session.get(Client, ODP_UI_DAP_CLIENT_ID) or Client(id=ODP_UI_DAP_CLIENT_ID)
    client.name = ODP_UI_DAP_CLIENT_NAME,
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


def sync_cli_client():
    """Create or update the Swagger UI client."""
    client = Session.get(Client, ODP_CLI_CLIENT_ID) or Client(id=ODP_CLI_CLIENT_ID)
    client.name = ODP_CLI_CLIENT_NAME,
    client.scopes = [Session.get(Scope, s.value) for s in ODPScope]
    client.save()

    hydra_admin_api.create_or_update_client(
        id=ODP_CLI_CLIENT_ID,
        name=ODP_CLI_CLIENT_NAME,
        secret=ODP_CLI_CLIENT_SECRET,
        scope_ids=[s.value for s in ODPScope],
        grant_types=[GrantType.CLIENT_CREDENTIALS],
    )


def create_admin_user():
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


if __name__ == '__main__':
    print('Initializing static system data...')
    create_schema()
    with Session.begin():
        sync_system_scopes()
        sync_admin_role()
        sync_admin_client()
        sync_dap_client()
        sync_cli_client()
        create_admin_user()
    print('Done.')
