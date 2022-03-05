from enum import Enum


class SchemaType(str, Enum):
    metadata = 'metadata'
    flag = 'flag'
    tag = 'tag'
    catalogue = 'catalogue'

    def __repr__(self):
        return repr(self.value)


class ScopeType(str, Enum):
    odp = 'odp'
    oauth = 'oauth'
    client = 'client'

    def __repr__(self):
        return repr(self.value)


class AuditCommand(str, Enum):
    insert = 'insert'
    update = 'update'
    delete = 'delete'

    def __repr__(self):
        return repr(self.value)
