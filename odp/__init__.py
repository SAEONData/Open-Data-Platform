from enum import Enum

import odp.config
import odp.db

__version__ = '2.0.0'

ODP_ADMIN_ROLE = 'odp.admin'


class ODPScope(str, Enum):
    CATALOGUE_MANAGE = 'odp.catalogue:manage'
    CATALOGUE_VIEW = 'odp.catalogue:view'
    CLIENT_MANAGE = 'odp.client:manage'
    CLIENT_VIEW = 'odp.client:view'
    COLLECTION_MANAGE = 'odp.collection:manage'
    COLLECTION_VIEW = 'odp.collection:view'
    RECORD_MANAGE = 'odp.record:manage'
    RECORD_VIEW = 'odp.record:view'
    PROJECT_MANAGE = 'odp.project:manage'
    PROJECT_VIEW = 'odp.project:view'
    PROVIDER_MANAGE = 'odp.provider:manage'
    PROVIDER_VIEW = 'odp.provider:view'
    ROLE_MANAGE = 'odp.role:manage'
    ROLE_VIEW = 'odp.role:view'
    SCOPE_MANAGE = 'odp.scope:manage'
    SCOPE_VIEW = 'odp.scope:view'
    USER_MANAGE = 'odp.user:manage'
    USER_VIEW = 'odp.user:view'
