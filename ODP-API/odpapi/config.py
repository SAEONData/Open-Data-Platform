from typing import Optional, List, Union, Literal
from enum import Enum

from pydantic import BaseSettings, AnyHttpUrl, validator, constr


class ServerEnv(str, Enum):
    development = 'development'
    testing = 'testing'
    staging = 'staging'
    production = 'production'


class AppConfig(BaseSettings):
    """
    Application config, populated from the environment.
    """
    SERVER_ENV: ServerEnv
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''
    ALLOW_ORIGINS: List[Union[Literal['*'], AnyHttpUrl]] = []
    ACCOUNTS_API_URL: Optional[AnyHttpUrl]
    NO_AUTH: Optional[bool]

    @validator('NO_AUTH', pre=True, always=True)
    def validate_no_auth(cls, value):
        return value

    @validator('ACCOUNTS_API_URL', always=True)
    def require_auth_settings(cls, value, values):
        if not values.get('NO_AUTH', False) and not value:
            raise ValueError("Value is required if NO_AUTH is False")
        return value


class RouterConfig(BaseSettings):
    """
    Router config base class. Router-specific descendants are created dynamically
    using the factory method below.
    """
    # class name of the adapter that will fulfil requests to this router
    ADAPTER: str
    # scope applicable to this router
    OAUTH2_SCOPE: str
    # roles that may read resources (belonging to the same institution, if the router is institution-aware)
    READONLY_ROLES: List[str] = []
    # roles that may read or write resources (belonging to the same institution, if the router is institution-aware)
    READWRITE_ROLES: List[str] = []
    # roles that may read or write resources belonging to any institution, and that may access admin-only functions
    ADMIN_ROLES: List[str] = []


def router_config_factory(router_module: str):
    router_name = router_module.rpartition('.')[2]
    config_cls = type('SettingsConfig', (), {'env_prefix': router_name.upper() + '.'})
    cls = type(router_name.title() + 'RouterConfig', (RouterConfig,), {'Config': config_cls})
    return cls()
