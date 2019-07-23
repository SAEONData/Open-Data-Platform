import pkg_resources
from typing import List, Dict, Any

import yaml
from pydantic import BaseModel, IPvAnyAddress


CONFIG_FILE = pkg_resources.resource_filename(__name__, '../config.yml')


class ServerConfig(BaseModel):
    host: IPvAnyAddress
    port: int


class AdapterConfig(BaseModel):
    name: str
    routes: List[str]
    config: Dict[str, Any] = {}


class AppConfig(BaseModel):
    server: ServerConfig
    adapters: List[AdapterConfig]


def read_config():
    with open(CONFIG_FILE, 'r') as f:
        config = AppConfig(**yaml.safe_load(f))
    return config
