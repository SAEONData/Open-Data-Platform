#!/usr/bin/env python
"""
This script creates any new tables and inserts any new static data.
Existing tables and data are not affected.

An admin user is created with prompts if not found.
"""

import pathlib
import sys
import uuid
from getpass import getpass

import argon2
from sqlalchemy import text

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

import odp


def create_odp_schema():
    """Create the ODP database schema.

    Only tables that do not exist are created. To modify existing table
    definitions, use Alembic migrations.
    """
    import odp.db.models
    odp.db.Base.metadata.create_all(odp.db.engine)


def create_odp_scopes():
    """Create any ODP system scopes that do not exist."""
    with odp.db.engine.begin() as conn:
        scopes = ','.join(f"('{s.value}')" for s in odp.ODPScope)
        conn.execute(text(f"INSERT INTO scope (id) VALUES {scopes} "
                          "ON CONFLICT DO NOTHING"))


def create_odp_admin_role():
    """Create the ODP admin role if it does not exist."""
    with odp.db.engine.begin() as conn:
        conn.execute(text("INSERT INTO role (id, name) VALUES "
                          f"('{odp.ODP_ADMIN_ROLE}', 'ODP Admin') "
                          "ON CONFLICT DO NOTHING"))

        role_scopes = ','.join(f"('{odp.ODP_ADMIN_ROLE}', '{s.value}')" for s in odp.ODPScope)
        conn.execute(text(f"INSERT INTO role_scope (role_id, scope_id) VALUES {role_scopes} "
                          "ON CONFLICT DO NOTHING"))


def create_odp_admin_user():
    """Create an admin user if one is not found."""
    with odp.db.engine.begin() as conn:
        result = conn.execute(text(f"SELECT 1 FROM user_role WHERE role_id = '{odp.ODP_ADMIN_ROLE}'"))

        if result.first() is None:
            print('Creating an admin user...')
            user_id = str(uuid.uuid4())
            while not (name := input('Full name: ')):
                pass
            while not (email := input('Email: ')):
                pass
            while not (password := getpass()):
                pass
            ph = argon2.PasswordHasher()
            password = ph.hash(password)

            conn.execute(text('INSERT INTO "user" (id, name, email, password, active, verified) VALUES '
                              f"('{user_id}', '{name}', '{email}', '{password}', true, true)"))

            conn.execute(text("INSERT INTO user_role (user_id, role_id) VALUES "
                              f"('{user_id}', '{odp.ODP_ADMIN_ROLE}')"))


def create_odp_app_client():
    """Create client config for the ODP app."""
    with odp.db.engine.begin() as conn:
        client_id = odp.config.config.ODP.APP.CLIENT_ID
        conn.execute(text("INSERT INTO client (id, name) VALUES "
                          f"('{client_id}', '(: The Open Data Platform App :)') "
                          "ON CONFLICT DO NOTHING"))

        client_scopes = ','.join(f"('{client_id}', '{s.value}')" for s in odp.ODPScope)
        conn.execute(text(f"INSERT INTO client_scope (client_id, scope_id) VALUES {client_scopes} "
                          "ON CONFLICT DO NOTHING"))


if __name__ == '__main__':
    create_odp_schema()
    create_odp_scopes()
    create_odp_admin_role()
    create_odp_admin_user()
    create_odp_app_client()
