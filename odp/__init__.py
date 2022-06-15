from enum import Enum

__version__ = '2.0.0'

DOI_PREFIX = 10.15493


class ODPScope(str, Enum):
    CATALOG_READ = 'odp.catalog:read'
    CLIENT_ADMIN = 'odp.client:admin'
    CLIENT_READ = 'odp.client:read'
    COLLECTION_ADMIN = 'odp.collection:admin'
    COLLECTION_READ = 'odp.collection:read'
    COLLECTION_TAG_ARCHIVE = 'odp.collection_tag:archive'
    COLLECTION_TAG_PUBLISH = 'odp.collection_tag:publish'
    PROJECT_ADMIN = 'odp.project:admin'
    PROJECT_READ = 'odp.project:read'
    PROVIDER_ADMIN = 'odp.provider:admin'
    PROVIDER_READ = 'odp.provider:read'
    RECORD_ADMIN = 'odp.record:admin'
    RECORD_READ = 'odp.record:read'
    RECORD_WRITE = 'odp.record:write'
    RECORD_TAG_QC = 'odp.record_tag:qc'
    RECORD_TAG_EMBARGO = 'odp.record_tag:embargo'
    RECORD_TAG_MIGRATED = 'odp.record_tag:migrated'
    ROLE_ADMIN = 'odp.role:admin'
    ROLE_READ = 'odp.role:read'
    SCHEMA_READ = 'odp.schema:read'
    SCOPE_READ = 'odp.scope:read'
    TAG_READ = 'odp.tag:read'
    USER_ADMIN = 'odp.user:admin'
    USER_READ = 'odp.user:read'


class ODPCollectionTag(str, Enum):
    ARCHIVE = 'collection-archive'
    PUBLISH = 'collection-publish'


class ODPRecordTag(str, Enum):
    QC = 'record-qc'
    EMBARGO = 'record-embargo'
    MIGRATED = 'record-migrated'


class ODPMetadataSchema(str, Enum):
    DATACITE4_SAEON = 'datacite4-saeon'
    ISO19115_SAEON = 'iso19115-saeon'


class ODPTagSchema(str, Enum):
    GENERIC = 'generic-tag'
    RECORD_QC = 'record-qc-tag'
    RECORD_EMBARGO = 'record-embargo-tag'
    RECORD_MIGRATED = 'record-migrated-tag'


class ODPCatalogSchema(str, Enum):
    SAEON = 'saeon-catalog'


class ODPCatalog(str, Enum):
    SAEON = 'SAEON'
