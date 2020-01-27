from typing import Optional
from enum import Enum

from pydantic import BaseSettings, AnyHttpUrl, validator


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

    NO_AUTH: Optional[bool]
    HYDRA_ADMIN_URL: Optional[AnyHttpUrl]
    OAUTH2_AUDIENCE: Optional[str]

    @validator('NO_AUTH', pre=True, always=True)
    def validate_no_auth(cls, value):
        return value

    @validator('HYDRA_ADMIN_URL', 'OAUTH2_AUDIENCE', always=True)
    def require_auth_settings(cls, value, values):
        if not values.get('NO_AUTH', False) and not value:
            raise ValueError("Value is required if NO_AUTH is False")
        return value

    class Config:
        env_prefix = ''
