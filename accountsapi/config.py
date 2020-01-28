from enum import Enum

from pydantic import BaseSettings, AnyHttpUrl


class ServerEnv(str, Enum):
    development = 'development'
    testing = 'testing'
    staging = 'staging'
    production = 'production'


class Config(BaseSettings):
    """
    Application config, populated from the environment.
    """
    SERVER_ENV: ServerEnv
    SERVER_HOST: str
    SERVER_PORT: int
    HYDRA_ADMIN_URL: AnyHttpUrl
