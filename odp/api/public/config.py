from typing import List, Union, Literal

from pydantic import BaseSettings, AnyHttpUrl

from odp.api.config import APIConfig


class PublicAPIConfig(APIConfig):
    """ Config specific to the public API """
    ALLOW_ORIGINS: List[Union[Literal['*'], AnyHttpUrl]] = []


class RouterConfig(BaseSettings):
    """ Router config base class. Router-specific descendants are created
    dynamically using the factory method below.
    """
    # class name of the adapter that will fulfil requests to this router
    ADAPTER: str


def router_config_factory(router_module: str):
    router_name = router_module.rpartition('.')[2]
    config_cls = type('SettingsConfig', (), {'env_prefix': router_name.upper() + '.'})
    cls = type(router_name.title() + 'RouterConfig', (RouterConfig,), {'Config': config_cls})
    return cls()
