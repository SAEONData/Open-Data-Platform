#!/usr/bin/env python
"""
Script for creating the ODP database schema and initializing
static data. Existing tables and data are not affected.
"""

import pathlib
import sys

from sqlalchemy import text

rootdir = pathlib.Path(__file__).parent.parent.parent
sys.path.append(str(rootdir))

import odp.db.models


def create_schema():
    odp.db.Base.metadata.create_all(odp.db.engine)


def create_scopes():
    scopes = ','.join(f"('{s.value}')" for s in odp.ODPScope)
    with odp.db.engine.begin() as conn:
        conn.execute(text(f"INSERT INTO scope (key) VALUES {scopes} "
                          "ON CONFLICT DO NOTHING"))


def create_sysadmin():
    with odp.db.engine.begin() as conn:
        conn.execute(text("INSERT INTO role (key, name) VALUES "
                          "('sysadmin', 'System Administrator') "
                          "ON CONFLICT DO NOTHING"))
        conn.execute(text("INSERT INTO role_scope (role_id, scope_id) "
                          "SELECT r.id, s.id FROM role r, scope s "
                          "WHERE r.key = 'sysadmin' "
                          "ON CONFLICT DO NOTHING"))


if __name__ == "__main__":
    create_schema()
    create_scopes()
    create_sysadmin()
