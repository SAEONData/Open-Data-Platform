import pkg_resources
from typing import List, Dict, Any, Union
from enum import Enum

import yaml
from pydantic import BaseModel, IPvAnyAddress, UrlStr, constr


CONFIG_FILE = pkg_resources.resource_filename(__name__, '../config.yml')
HOSTNAME_REGEX = r'^\w+(\.\w+)+$'


class RunEnviron(str, Enum):
    development = 'development'
    test = 'test'
    staging = 'staging'
    production = 'production'


class ServerConfig(BaseModel):
    """
    ASGI server config.
    """
    host: Union[IPvAnyAddress, constr(regex=HOSTNAME_REGEX)]
    port: int


class SecurityConfig(BaseModel):
    """
    Security-related config.
    """
    hydra_admin_url: UrlStr
    hydra_dev_server: bool = False
    oauth2_audience: str
    no_access_token_validation: bool = False


class AdapterConfig(BaseModel):
    """
    Config for an individual adapter.
    """
    name: str
    routes: List[str]
    config: Dict[str, Any] = {}


class AppConfig(BaseModel):
    """
    Top-level config container class.
    """
    environment: RunEnviron
    server: ServerConfig
    security: SecurityConfig
    adapters: List[AdapterConfig]


def read_config():
    with open(CONFIG_FILE, 'r') as f:
        config = AppConfig(**yaml.safe_load(f))
    return config
