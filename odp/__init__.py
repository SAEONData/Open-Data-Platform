from enum import Enum

__version__ = '2.0.0'

DOI_PREFIX = 10.15493


class ODPScope(str, Enum):
    CATALOG_READ = 'odp.catalog:read'
    CLIENT_ADMIN = 'odp.client:admin'
    CLIENT_READ = 'odp.client:read'
    COLLECTION_ADMIN = 'odp.collection:admin'
    COLLECTION_READ = 'odp.collection:read'
    COLLECTION_PROJECT = 'odp.collection:project'
    COLLECTION_NOINDEX = 'odp.collection:noindex'
    PROVIDER_ADMIN = 'odp.provider:admin'
    PROVIDER_READ = 'odp.provider:read'
    RECORD_ADMIN = 'odp.record:admin'
    RECORD_READ = 'odp.record:read'
    RECORD_WRITE = 'odp.record:write'
    RECORD_QC = 'odp.record:qc'
    RECORD_EMBARGO = 'odp.record:embargo'
    RECORD_MIGRATE = 'odp.record:migrate'
    RECORD_NOINDEX = 'odp.record:noindex'
    RECORD_RETRACT = 'odp.record:retract'
    RECORD_NOTE = 'odp.record:note'
    ROLE_ADMIN = 'odp.role:admin'
    ROLE_READ = 'odp.role:read'
    SCHEMA_READ = 'odp.schema:read'
    SCOPE_READ = 'odp.scope:read'
    TAG_READ = 'odp.tag:read'
    TOKEN_READ = 'odp.token:read'
    USER_ADMIN = 'odp.user:admin'
    USER_READ = 'odp.user:read'
    VOCABULARY_INFRASTRUCTURE = 'odp.vocabulary:infrastructure'
    VOCABULARY_PROJECT = 'odp.vocabulary:project'
    VOCABULARY_READ = 'odp.vocabulary:read'


class ODPCollectionTag(str, Enum):
    READY = 'Collection.Ready'
    FROZEN = 'Collection.Frozen'
    INFRASTRUCTURE = 'Collection.Infrastructure'
    PROJECT = 'Collection.Project'
    NOTINDEXED = 'Collection.NotIndexed'


class ODPRecordTag(str, Enum):
    QC = 'Record.QC'
    EMBARGO = 'Record.Embargo'
    MIGRATED = 'Record.Migrated'
    NOTINDEXED = 'Record.NotIndexed'
    RETRACTED = 'Record.Retracted'
    NOTE = 'Record.Note'


class ODPMetadataSchema(str, Enum):
    SAEON_DATACITE_4 = 'SAEON.DataCite.4'
    SAEON_ISO19115 = 'SAEON.ISO19115'
    DATACITE_4_3 = 'DataCite.4.3'


class ODPTagSchema(str, Enum):
    GENERIC = 'Tag.Generic'
    COLLECTION_INFRASTRUCTURE = 'Tag.Collection.Infrastructure'
    COLLECTION_PROJECT = 'Tag.Collection.Project'
    RECORD_QC = 'Tag.Record.QC'
    RECORD_EMBARGO = 'Tag.Record.Embargo'
    RECORD_MIGRATED = 'Tag.Record.Migrated'


class ODPCatalog(str, Enum):
    SAEON = 'SAEON'
    DATACITE = 'DataCite'


class ODPVocabulary(str, Enum):
    INFRASTRUCTURE = 'Infrastructure'
    PROJECT = 'Project'


class ODPVocabularySchema(str, Enum):
    INFRASTRUCTURE = 'Vocabulary.Infrastructure'
    PROJECT = 'Vocabulary.Project'
