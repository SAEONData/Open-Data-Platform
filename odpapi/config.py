import pkg_resources
from typing import List, Dict, Any, Union

import yaml
from pydantic import BaseModel, IPvAnyAddress, UrlStr, constr


CONFIG_FILE = pkg_resources.resource_filename(__name__, '../config.yml')
HOSTNAME_REGEX = r'^\w+(\.\w+)+$'


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
    hydra_insecure_server: bool = False
    hydra_admin_url: UrlStr
    required_audience: str


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
    server: ServerConfig
    security: SecurityConfig
    adapters: List[AdapterConfig]


def read_config():
    with open(CONFIG_FILE, 'r') as f:
        config = AppConfig(**yaml.safe_load(f))
    return config
