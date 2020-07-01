import importlib
import inspect
import pkgutil

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

import odp.api.public.adapters
from odp.api.public.adapter import ODPAPIAdapter, ODPAPIAdapterConfig
from odp.api.public.config import router_config_factory


def load_adapters(app: FastAPI):
    adapter_classes = {}
    config_classes = {}
    for module_info in pkgutil.iter_modules(odp.api.public.adapters.__path__, odp.api.public.adapters.__name__ + '.'):
        module = importlib.import_module(module_info.name)
        adapter_classes.update({
            name: cls for (name, cls) in inspect.getmembers(module, lambda x: inspect.isclass(x) and
                                                                              x is not ODPAPIAdapter and
                                                                              issubclass(x, ODPAPIAdapter))
        })
        config_classes.update({
            name: cls for (name, cls) in inspect.getmembers(module, lambda x: inspect.isclass(x) and
                                                                              x is not ODPAPIAdapterConfig and
                                                                              issubclass(x, ODPAPIAdapterConfig))
        })

    adapters = {}
    for adapter_name, adapter_cls in adapter_classes.items():
        config_name = adapter_name + 'Config'
        config_cls = config_classes[config_name]
        adapters[adapter_name] = adapter_cls(app, config_cls())

    app.extra['adapters'] = adapters


def load_configs(app: FastAPI, *router_modules: str):
    router_configs = {}
    for router_module in router_modules:
        router_configs[router_module] = router_config_factory(router_module)
    app.extra['router_configs'] = router_configs


async def set_config(request: Request):
    """
    Dependency function which sets the router config for the current request.
    Route functions can retrieve this from ``request.state.config``.
    """
    router_module = request.scope['endpoint'].__module__
    try:
        request.state.config = request.app.extra['router_configs'][router_module]
    except KeyError:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Router config for {router_module} has not been loaded.")


async def set_adapter(request: Request):
    """
    Dependency function which sets the adapter for the current request.
    Route functions can retrieve this from ``request.state.adapter``.

    Note: the set_config dependency must come before this one
    """
    router_module = request.scope['endpoint'].__module__
    try:
        request.state.adapter = request.app.extra['adapters'][request.state.config.ADAPTER]
    except KeyError:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Unknown adapter {request.state.config.ADAPTER} specified for {router_module}.")
