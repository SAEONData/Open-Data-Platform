from enum import Enum


class SchemaType(str, Enum):
    metadata = 'metadata'
    tag = 'tag'
    vocabulary = 'vocabulary'

    def __repr__(self):
        return repr(self.value)


class ScopeType(str, Enum):
    odp = 'odp'
    oauth = 'oauth'
    client = 'client'

    def __repr__(self):
        return repr(self.value)


class TagType(str, Enum):
    collection = 'collection'
    record = 'record'

    def __repr__(self):
        return repr(self.value)


class TagCardinality(str, Enum):
    one = 'one'  # one tag instance per object
    user = 'user'  # one tag instance per user per object
    multi = 'multi'  # multiple tag instances per user per object

    def __repr__(self):
        return repr(self.value)


class AuditCommand(str, Enum):
    insert = 'insert'
    update = 'update'
    delete = 'delete'

    def __repr__(self):
        return repr(self.value)
