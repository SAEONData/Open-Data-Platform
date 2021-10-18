#!/usr/bin/env python
"""
This script creates the ODP database schema, static data, and initial
configuration data - including an admin user (with prompts).

The script may be re-run as needed to insert any new static/config data.
Existing tables and data are not affected.
"""

import pathlib
import sys
import uuid
from getpass import getpass

import argon2
from sqlalchemy import select

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

from odp import ODPScope
from odp.db import engine, Session, Base
from odp.db.models import Scope, Role, RoleScope, UserRole, User, Client, ClientScope

ODP_ADMIN_ROLE = 'ODP:Admin'
ODP_APP_CLIENT_ID = 'odp.saeon.ac.za'


def create_schema():
    """Create the ODP database schema.

    Only tables that do not exist are created. To modify existing table
    definitions, use Alembic migrations.
    """
    Base.metadata.create_all(engine)


def create_scopes(session):
    """Create any ODP system scopes that do not exist."""
    for odp_scope in ODPScope:
        if not session.get(Scope, odp_scope.value):
            scope = Scope(id=odp_scope.value)
            session.add(scope)


def create_admin_role(session):
    """Create the ODP admin role if it does not exist."""
    if not session.get(Role, ODP_ADMIN_ROLE):
        role = Role(id=ODP_ADMIN_ROLE)
        session.add(role)

    for odp_scope in ODPScope:
        if not session.get(RoleScope, (ODP_ADMIN_ROLE, odp_scope.value)):
            role_scope = RoleScope(
                role_id=ODP_ADMIN_ROLE,
                scope_id=odp_scope.value,
            )
            session.add(role_scope)


def create_admin_user(session):
    """Create an admin user if one is not found."""
    if not session.execute(
            select(UserRole).where(UserRole.role_id == ODP_ADMIN_ROLE)
    ).first():
        print('Creating an admin user...')
        while not (name := input('Full name: ')):
            pass
        while not (email := input('Email: ')):
            pass
        while not (password := getpass()):
            pass

        user_id = str(uuid.uuid4())
        password = argon2.PasswordHasher().hash(password)

        user = User(
            id=user_id,
            name=name,
            email=email,
            password=password,
            active=True,
            verified=True,
        )
        session.add(user)

        user_role = UserRole(
            user_id=user_id,
            role_id=ODP_ADMIN_ROLE,
        )
        session.add(user_role)


def create_app_client(session):
    """Create client config for the ODP app."""
    if not session.get(Client, ODP_APP_CLIENT_ID):
        client = Client(
            id=ODP_APP_CLIENT_ID,
            name='The Open Data Platform Web UI',
        )
        session.add(client)

    for odp_scope in ODPScope:
        if not session.get(ClientScope, (ODP_APP_CLIENT_ID, odp_scope.value)):
            client_scope = ClientScope(
                client_id=ODP_APP_CLIENT_ID,
                scope_id=odp_scope.value,
            )
            session.add(client_scope)


if __name__ == '__main__':
    create_schema()
    with Session() as sess, sess.begin():
        create_scopes(sess)
        create_admin_role(sess)
        create_admin_user(sess)
        create_app_client(sess)
