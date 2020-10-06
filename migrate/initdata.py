#!/usr/bin/env python

"""Initialize ODP static data."""

from sqlalchemy.exc import IntegrityError


def initialize_roles():
    rows = [
        {'key': 'admin', 'name': 'Admin', 'admin': True},
        {'key': 'curator', 'name': 'Curator', 'admin': True},
        {'key': 'contributor', 'name': 'Contributor', 'admin': False},
        {'key': 'member', 'name': 'Member', 'admin': False},
    ]
    for row in rows:
        key = row['key']
        name = row['name']
        admin = row['admin']
        try:
            conn.execute("INSERT INTO role (key, name, admin) "
                         f"VALUES ('{key}', '{name}', {admin})")
        except IntegrityError:
            conn.execute(f"UPDATE role SET name='{name}', admin={admin} "
                         f"WHERE key='{key}'")


def initialize_scopes():
    rows = [
        {'key': 'ODP.Admin', 'description': 'Platform administration functions'},
        {'key': 'ODP.Metadata', 'description': 'Metadata management functions'},
        {'key': 'SAEON.Observations.WebAPI', 'description': 'The SAEON Observations Database'},
    ]
    for row in rows:
        key = row['key']
        description = row['description']
        try:
            conn.execute("INSERT INTO scope (key, description) "
                         f"VALUES ('{key}', '{description}')")
        except IntegrityError:
            conn.execute(f"UPDATE scope SET description='{description}' "
                         f"WHERE key='{key}'")


def initialize_capabilities():
    capabilities = {
        'ODP.Admin': ['admin', 'member'],
        'ODP.Metadata': ['admin', 'curator', 'contributor', 'member'],
        'SAEON.Observations.WebAPI': ['admin', 'contributor'],
    }
    for scope, roles in capabilities.items():
        for role in roles:
            conn.execute("INSERT INTO capability (scope_id, role_id) "
                         "SELECT s.id, r.id FROM scope s, role r "
                         f"WHERE s.key = '{scope}' AND r.key = '{role}' "
                         "ON CONFLICT DO NOTHING")


if __name__ == "__main__":
    from odp.db import engine

    conn = engine.connect()
    initialize_roles()
    initialize_scopes()
    initialize_capabilities()