import uuid
from enum import Enum

from sqlalchemy import text

import odp.config
import odp.db

__version__ = '2.0.0'

ODP_ADMIN_ROLE = 'odp.admin'


class ODPScope(str, Enum):
    CATALOGUE_MANAGE = 'odp.catalogue:manage'
    CATALOGUE_VIEW = 'odp.catalogue:view'
    CLIENT_MANAGE = 'odp.client:manage'
    CLIENT_VIEW = 'odp.client:view'
    COLLECTION_MANAGE = 'odp.collection:manage'
    COLLECTION_VIEW = 'odp.collection:view'
    RECORD_MANAGE = 'odp.record:manage'
    RECORD_VIEW = 'odp.record:view'
    PROJECT_MANAGE = 'odp.project:manage'
    PROJECT_VIEW = 'odp.project:view'
    PROVIDER_MANAGE = 'odp.provider:manage'
    PROVIDER_VIEW = 'odp.provider:view'
    ROLE_MANAGE = 'odp.role:manage'
    ROLE_VIEW = 'odp.role:view'
    SCOPE_MANAGE = 'odp.scope:manage'
    SCOPE_VIEW = 'odp.scope:view'
    USER_MANAGE = 'odp.user:manage'
    USER_VIEW = 'odp.user:view'


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
        scopes = ','.join(f"('{s.value}')" for s in ODPScope)
        conn.execute(text(f"INSERT INTO scope (id) VALUES {scopes} "
                          "ON CONFLICT DO NOTHING"))


def create_odp_admin_role():
    """Create the ODP admin role if it does not exist."""
    with odp.db.engine.begin() as conn:
        conn.execute(text("INSERT INTO role (id, name) VALUES "
                          f"('{ODP_ADMIN_ROLE}', 'ODP Admin') "
                          "ON CONFLICT DO NOTHING"))

        role_scopes = ','.join(f"('{ODP_ADMIN_ROLE}', '{s.value}')" for s in ODPScope)
        conn.execute(text(f"INSERT INTO role_scope (role_id, scope_id) VALUES {role_scopes} "
                          "ON CONFLICT DO NOTHING"))


def create_odp_admin_user():
    """Ensure that there is an admin user."""
    with odp.db.engine.begin() as conn:
        result = conn.execute(text(f"SELECT 1 FROM user_role WHERE role_id = '{ODP_ADMIN_ROLE}'"))

        if result.first() is None:
            user_id = str(uuid.uuid4())
            email = input("Enter the admin user's email address: ")

            conn.execute(text('INSERT INTO "user" (id, email, active, verified) VALUES '
                              f"('{user_id}', '{email}', true, true) "
                              "ON CONFLICT DO NOTHING"))

            conn.execute(text('INSERT INTO user_role (user_id, role_id) '
                              f"SELECT u.id, '{ODP_ADMIN_ROLE}' FROM \"user\" u "
                              f"WHERE u.email = '{email}'"))


def create_odp_app_client():
    """Create client config for the ODP app."""
    with odp.db.engine.begin() as conn:
        client_id = odp.config.config.ODP.APP.CLIENT_ID
        conn.execute(text("INSERT INTO client (id, name) VALUES "
                          f"('{client_id}', '(: The Open Data Platform App :)') "
                          "ON CONFLICT DO NOTHING"))

        client_scopes = ','.join(f"('{client_id}', '{s.value}')" for s in ODPScope)
        conn.execute(text(f"INSERT INTO client_scope (client_id, scope_id) VALUES {client_scopes} "
                          "ON CONFLICT DO NOTHING"))
