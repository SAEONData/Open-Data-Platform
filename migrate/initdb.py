#!/usr/bin/env python
"""
This script creates the ODP database schema and initializes
static and administrative data.

An admin user is created, with prompts, if not found.
"""

import pathlib
import sys
import uuid
from getpass import getpass

import argon2
import yaml
from sqlalchemy import select

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

from odp import ODPScope
from odp.db import engine, Session, Base
from odp.db.models import (
    Client,
    ClientScope,
    Collection,
    Project,
    Provider,
    Role,
    RoleScope,
    Scope,
    User,
    UserRole,
)

datadir = pathlib.Path(__file__).parent / 'data'

ODP_ADMIN_ROLE = 'ODP:Admin'
ODP_APP_CLIENT_ID = 'odp.saeon.ac.za'


def create_schema():
    """Create the ODP database schema.

    Only tables that do not exist are created. To modify existing table
    definitions, use Alembic migrations.
    """
    Base.metadata.create_all(engine)


def create_scopes():
    """Create any ODP system scopes that do not exist."""
    for odp_scope in ODPScope:
        if not Session.get(Scope, odp_scope.value):
            scope = Scope(id=odp_scope.value)
            scope.save()


def create_admin_role():
    """Create the ODP admin role if it does not exist."""
    if not Session.get(Role, ODP_ADMIN_ROLE):
        role = Role(id=ODP_ADMIN_ROLE)
        role.save()

    for odp_scope in ODPScope:
        if not Session.get(RoleScope, (ODP_ADMIN_ROLE, odp_scope.value)):
            role_scope = RoleScope(
                role_id=ODP_ADMIN_ROLE,
                scope_id=odp_scope.value,
            )
            role_scope.save()


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
        user.save()

        user_role = UserRole(
            user_id=user_id,
            role_id=ODP_ADMIN_ROLE,
        )
        user_role.save()


def create_app_client():
    """Create client config for the ODP app."""
    if not Session.get(Client, ODP_APP_CLIENT_ID):
        client = Client(
            id=ODP_APP_CLIENT_ID,
            name='The Open Data Platform Web UI',
        )
        client.save()

    for odp_scope in ODPScope:
        if not Session.get(ClientScope, (ODP_APP_CLIENT_ID, odp_scope.value)):
            client_scope = ClientScope(
                client_id=ODP_APP_CLIENT_ID,
                scope_id=odp_scope.value,
            )
            client_scope.save()


def create_roles():
    """Create or update role definitions."""
    with open(datadir / 'roles.yml') as f:
        role_data = yaml.safe_load(f)

    for role_id, role_spec in role_data.items():
        role = Session.get(Role, role_id) or Role(id=role_id)
        role.scopes = [Session.get(Scope, scope_id) for scope_id in role_spec['scopes']]
        role.save()


def create_projects():
    """Create or update project definitions."""
    with open(datadir / 'projects.yml') as f:
        project_data = yaml.safe_load(f)

    for project_id, project_spec in project_data.items():
        project = Session.get(Project, project_id) or Project(id=project_id)
        project.name = project_spec['name']
        project.save()


def create_providers_and_collections():
    """Create or update providers, collections and project-collection
    associations."""
    with open(datadir / 'providers_collections.yml') as f:
        provider_collection_data = yaml.safe_load(f)

    for provider_id, provider_spec in provider_collection_data.items():
        provider = Session.get(Provider, provider_id) or Provider(id=provider_id)
        provider.name = provider_spec['name']
        provider.save()
        for collection_id, collection_spec in provider_spec['collections'].items():
            collection = Session.get(Collection, collection_id) or Collection(id=collection_id)
            collection.name = collection_spec['name']
            collection.doi_key = collection_spec.get('doi_key')
            collection.provider_id = provider_id
            collection.projects = [Session.get(Project, project_id) for project_id in collection_spec['projects']]
            collection.save()


if __name__ == '__main__':
    create_schema()
    with Session.begin():
        create_scopes()
        create_admin_role()
        create_admin_user()
        create_app_client()
        create_roles()
        create_projects()
        create_providers_and_collections()
