from enum import Enum


class SchemaType(str, Enum):
    catalogue = 'catalogue'
    metadata = 'metadata'
    tag = 'tag'
