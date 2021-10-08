from enum import Enum


class RoleType(str, Enum):
    platform = 'platform'
    client = 'client'
    project = 'project'
    provider = 'provider'


class SchemaType(str, Enum):
    catalogue = 'catalogue'
    metadata = 'metadata'
    tag = 'tag'
