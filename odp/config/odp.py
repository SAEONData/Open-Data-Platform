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


class ODPUIAdminConfig(BaseConfig, OAuth2ClientConfigMixin):
    class Config:
        env_prefix = 'ODP_UI_ADMIN_'

    FLASK_KEY: str       # Flask secret key
    API_URL: AnyHttpUrl  # URL of the ODP API


class ODPUIPublicConfig(BaseConfig, OAuth2ClientConfigMixin):
    class Config:
        env_prefix = 'ODP_UI_PUBLIC_'

    FLASK_KEY: str           # Flask secret key
    SERVER_NAME: str = None  # public domain name
    THREDDS_URL: AnyHttpUrl  # proxy URL for the THREDDS server


class ODPUIConfig(BaseConfig):
    _subconfig = {
        'ADMIN': ODPUIAdminConfig,
        'PUBLIC': ODPUIPublicConfig,
    }


class ODPIdentityConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_IDENTITY_'

    FLASK_KEY: str                     # Flask secret key
    LOGIN_EXPIRY: int                  # number of seconds to remember a successful login; 0 = remember indefinitely
    NCCRD_BRAND_CLIENT_ID: str = None  # OAuth2 client ID that will trigger NCCRD UI branding


class ODPMailConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_MAIL_'

    HOST: str             # mail server IP / hostname
    PORT: int = 25        # mail server port
    TLS: bool = False     # use TLS
    USERNAME: str = None  # sender email address
    PASSWORD: str = None  # sender password


class ODPPublishConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_PUBLISH_'

    # minimum interval in minutes before re-checking an already harvested metadata record
    HARVEST_CHECK_INTERVAL: int

    # maximum number of records to harvest or sync in a publishing run
    BATCH_SIZE: int


class ODPConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_'

    ENV: ServerEnv                # deployment environment
    LOG_LEVEL: LogLevel = 'info'  # logging detail level

    _subconfig = {
        'API': ODPAPIConfig,
        'DB': ODPDBConfig,
        'UI': ODPUIConfig,
        'IDENTITY': ODPIdentityConfig,
        'MAIL': ODPMailConfig,
        'PUBLISH': ODPPublishConfig,
    }
