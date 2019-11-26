import importlib
import pkgutil
import inspect
from typing import List

from starlette.requests import Request
from starlette.status import HTTP_501_NOT_IMPLEMENTED
from fastapi import HTTPException, FastAPI
from pydantic import BaseSettings

import odpapi_adapters


class ODPAPIAdapterConfig(BaseSettings):
    ROUTES: List[str]


class ODPAPIAdapter:
    def __init__(self, app: FastAPI, config: ODPAPIAdapterConfig):
        self.app = app
        self.config = config
        self.app_config = self.app.extra['config']


def get_adapter(request: Request):
    for adapter in request.app.extra['adapters']:
        for route in adapter.config.ROUTES:
            if request.url.path.startswith(route):
                return adapter
    raise HTTPException(status_code=HTTP_501_NOT_IMPLEMENTED, detail="Adapter not found for {}".format(request.url.path))


def load_adapters(app: FastAPI):
    installed_adapters = {}
    config_classes = {}
    for module_info in pkgutil.iter_modules(odpapi_adapters.__path__, odpapi_adapters.__name__ + '.'):
        module = importlib.import_module(module_info.name)
        installed_adapters.update({
            name: cls for (name, cls) in inspect.getmembers(module, lambda x: inspect.isclass(x) and
                                                                              x is not ODPAPIAdapter and
                                                                              issubclass(x, ODPAPIAdapter))
        })
        config_classes.update({
            name: cls for (name, cls) in inspect.getmembers(module, lambda x: inspect.isclass(x) and
                                                                              x is not ODPAPIAdapterConfig and
                                                                              issubclass(x, ODPAPIAdapterConfig))
        })

    adapters = []
    for adapter_name, adapter_cls in installed_adapters.items():
        config_name = adapter_name + 'Config'
        config_cls = config_classes[config_name]
        adapters += [adapter_cls(app, config_cls())]

    app.extra['adapters'] = adapters
