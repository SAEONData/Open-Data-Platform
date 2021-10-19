#!/usr/bin/env python
"""
This script can be used to initialize SAEON roles, projects,
providers and collections.
"""

import pathlib
import sys

import yaml

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

from odp.db import Session
from odp.db.models import Role, Scope, Project, Provider, Collection

datadir = pathlib.Path(__file__).parent / 'saeondata'


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
    with Session.begin():
        create_roles()
        create_projects()
        create_providers_and_collections()
