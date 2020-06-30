import importlib
import pkgutil
import inspect

from fastapi import FastAPI
from pydantic import BaseSettings

import odpapi_adapters


class ODPAPIAdapterConfig(BaseSettings):
    pass


class ODPAPIAdapter:
    def __init__(self, app: FastAPI, config: ODPAPIAdapterConfig):
        self.app = app
        self.config = config
        self.app_config = self.app.extra['config']


def load_adapters(app: FastAPI):
    adapter_classes = {}
    config_classes = {}
    for module_info in pkgutil.iter_modules(odpapi_adapters.__path__, odpapi_adapters.__name__ + '.'):
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
