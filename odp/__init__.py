from enum import Enum

__version__ = '2.0.0'


class ODPScope(str, Enum):
    CATALOGUE_MANAGE = 'ODP.catalogue:manage'
    CATALOGUE_VIEW = 'ODP.catalogue:view'
    CLIENT_MANAGE = 'ODP.client:manage'
    CLIENT_VIEW = 'ODP.client:view'
    COLLECTION_MANAGE = 'ODP.collection:manage'
    COLLECTION_VIEW = 'ODP.collection:view'
    RECORD_MANAGE = 'ODP.record:manage'
    RECORD_VIEW = 'ODP.record:view'
    PROJECT_MANAGE = 'ODP.project:manage'
    PROJECT_VIEW = 'ODP.project:view'
    PROVIDER_MANAGE = 'ODP.provider:manage'
    PROVIDER_VIEW = 'ODP.provider:view'
    ROLE_MANAGE = 'ODP.role:manage'
    ROLE_VIEW = 'ODP.role:view'
    SCOPE_MANAGE = 'ODP.scope:manage'
    SCOPE_VIEW = 'ODP.scope:view'
    USER_MANAGE = 'ODP.user:manage'
    USER_VIEW = 'ODP.user:view'
