from enum import Enum
from typing import List, Union, Literal

from pydantic import AnyHttpUrl, constr

from odp.config import BaseConfig
from odp.config.mixins import DBConfigMixin, OAuth2ClientConfigMixin


class ServerEnv(str, Enum):
    DEVELOPMENT = 'development'
    TESTING = 'testing'
    STAGING = 'staging'
    PRODUCTION = 'production'


class LogLevel(str, Enum):
    CRITICAL = 'critical'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    DEBUG = 'debug'


class ODPDBConfig(BaseConfig, DBConfigMixin):
    class Config:
        env_prefix = 'ODP_DB_'


class ODPAPIConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_API_'

    # (optional) URL path prefix at which the API is mounted, e.g. `/api`
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''

    # (optional) JSON-encoded list of allowed CORS origins; `["*"]` to allow any origin
    ALLOW_ORIGINS: List[Union[Literal['*'], AnyHttpUrl]] = []

    # URL of the ODP admin API, for token introspection
    ADMIN_API_URL: AnyHttpUrl


class ODPAdminUIConfig(BaseConfig, OAuth2ClientConfigMixin):
    class Config:
        env_prefix = 'ODP_ADMIN_UI_'

    FLASK_KEY: str  # Flask secret key
    THEME: str      # Flask-Admin theme; see https://bootswatch.com/ for options


class ODPAdminConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_ADMIN_'

    INSTITUTION: str  # institution key of the institution that owns the platform
    ROLE: str         # role key of the admin role
    SCOPE: str        # the admin scope

    _subconfig = {
        'UI': ODPAdminUIConfig,
    }


class ODPIdentityConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_IDENTITY_'

    FLASK_KEY: str     # Flask secret key
    LOGIN_EXPIRY: int  # number of seconds to remember a successful login; 0 = remember indefinitely


class ODPMailConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_MAIL_'

    HOST: str       # mail server IP
    PORT: int = 25  # mail server port


class ODPPublishConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_PUBLISH_'

    # minimum interval in minutes before re-checking an already harvested metadata record
    HARVEST_CHECK_INTERVAL: int

    # maximum number of records to harvest or sync in a given publishing run
    BATCH_SIZE: int

    # number of times to retry syncing (i.e. publishing/unpublishing) a record with
    # a given catalogue after failure
    MAX_RETRIES: int


class ODPConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_'

    ENV: ServerEnv                # deployment environment
    LOG_LEVEL: LogLevel = 'info'  # logging detail level

    _subconfig = {
        'API': ODPAPIConfig,
        'DB': ODPDBConfig,
        'ADMIN': ODPAdminConfig,
        'IDENTITY': ODPIdentityConfig,
        'MAIL': ODPMailConfig,
        'PUBLISH': ODPPublishConfig,
    }
