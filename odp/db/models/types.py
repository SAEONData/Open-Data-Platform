from enum import Enum


class SchemaType(str, Enum):
    catalogue = 'catalogue'
    metadata = 'metadata'
    tag = 'tag'

    def __repr__(self):
        return repr(self.value)


class AuditCommand(str, Enum):
    insert = 'insert'
    update = 'update'
    delete = 'delete'

    def __repr__(self):
        return repr(self.value)
