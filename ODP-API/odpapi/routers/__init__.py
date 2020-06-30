from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ..config import router_config_factory


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
