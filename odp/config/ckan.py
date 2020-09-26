from pydantic import AnyHttpUrl

from odp.config import BaseConfig
from odp.config.mixins import DBConfigMixin


class CKANDBConfig(BaseConfig, DBConfigMixin):
    class Config:
        env_prefix = 'CKAN_DB_'


class CKANConfig(BaseConfig):
    class Config:
        env_prefix = 'CKAN_'

    URL: AnyHttpUrl  # URL of the CKAN server

    _subconfig = {
        'DB': CKANDBConfig,
    }
