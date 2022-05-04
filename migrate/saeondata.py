#!/usr/bin/env python
"""
This script can be used to initialize SAEON admin data.
It should be run from the ../deploy or ../develop directory,
as applicable.
"""

import pathlib
import sys

import yaml

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

from odp.db import Session
from odp.db.models import Catalogue, Flag, Role, Schema, SchemaType, Scope, ScopeType, Tag

datadir = pathlib.Path(__file__).parent / 'saeondata'


def create_schemas():
    """Create or update schema definitions."""
    with open(datadir / 'schemas.yml') as f:
        schema_data = yaml.safe_load(f)

    for schema_id, schema_spec in schema_data.items():
        schema_type = schema_spec['type']
        schema = Session.get(Schema, (schema_id, schema_type)) or Schema(id=schema_id, type=schema_type)
        schema.uri = schema_spec['uri']
        schema.save()


def create_flags():
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


def create_tags():
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


def create_roles():
    """Create or update role definitions."""
    with open(datadir / 'roles.yml') as f:
        role_data = yaml.safe_load(f)

    for role_id, role_spec in role_data.items():
        role = Session.get(Role, role_id) or Role(id=role_id)
        role.scopes = [Session.get(Scope, (scope_id, ScopeType.odp)) for scope_id in role_spec['scopes']]
        role.save()


def create_catalogues():
    """Create or update catalogue definitions."""
    with open(datadir / 'catalogues.yml') as f:
        catalogue_data = yaml.safe_load(f)

    for catalogue_id, catalogue_spec in catalogue_data.items():
        catalogue = Session.get(Catalogue, catalogue_id) or Catalogue(id=catalogue_id)
        catalogue.schema_id = catalogue_spec['schema_id']
        catalogue.schema_type = SchemaType.catalogue
        catalogue.save()


if __name__ == '__main__':
    print('Initializing SAEON admin data...')
    with Session.begin():
        create_schemas()
        create_flags()
        create_tags()
        create_roles()
        create_catalogues()
    print('Done.')
