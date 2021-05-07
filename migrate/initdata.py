#!/usr/bin/env python

"""Initialize ODP static data."""

from sqlalchemy.exc import IntegrityError


def initialize_roles():
    rows = [
        {'key': 'admin', 'name': 'Admin', 'admin': True},
        {'key': 'curator', 'name': 'Curator', 'admin': True},
        {'key': 'harvester', 'name': 'Harvester', 'admin': False},
        {'key': 'contributor', 'name': 'Contributor', 'admin': False},
        {'key': 'manager', 'name': 'Manager', 'admin': False},
        {'key': 'staff', 'name': 'Staff', 'admin': False},
        {'key': 'datascientist', 'name': 'Data Scientist', 'admin': False},
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
        {'key': 'ODP.Catalogue', 'description': 'The ODP Metadata Catalogue'},
        {'key': 'SAEON.Observations.WebAPI', 'description': 'The SAEON Observations Database'},
        {'key': 'SAEON.DataPortal', 'description': 'The SAEON Data Portal'},
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
        'ODP.Admin': ['admin', 'manager', 'staff'],
        'ODP.Metadata': ['admin', 'curator', 'harvester', 'contributor', 'staff'],
        'ODP.Catalogue': ['harvester'],
        'SAEON.Observations.WebAPI': ['admin', 'staff'],
        'SAEON.DataPortal': ['admin', 'datascientist', 'curator', 'staff'],
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
