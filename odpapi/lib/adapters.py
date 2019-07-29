import importlib
import pkgutil
import inspect
from typing import List, Dict, Any

from starlette.requests import Request
from starlette.status import HTTP_501_NOT_IMPLEMENTED
from fastapi import HTTPException, FastAPI

import odpapi_adapters


class ODPAPIAdapter:
    def __init__(self, routes: List[str], **config: Dict[str, Any]):
        self.routes = routes


def get_adapter(request: Request):
    for adapter in request.app.extra['adapters']:
        for route in adapter.routes:
            if request.url.path.startswith(route):
                return adapter
    raise HTTPException(status_code=HTTP_501_NOT_IMPLEMENTED, detail="Adapter not found for {}".format(request.url.path))


def load_adapters(app: FastAPI):
    available_adapters = {}
    for module_info in pkgutil.iter_modules(odpapi_adapters.__path__, odpapi_adapters.__name__ + '.'):
        module = importlib.import_module(module_info.name)
        available_adapters.update({
            name: cls for (name, cls) in inspect.getmembers(module, lambda x: inspect.isclass(x) and
                                                                              x is not ODPAPIAdapter and
                                                                              issubclass(x, ODPAPIAdapter))
        })

    adapters = []
    unknowns = []
    for entry in app.extra['config'].adapters:
        if entry.name not in available_adapters:
            unknowns += [entry.name]
            continue
        adapter_cls = available_adapters[entry.name]
        adapters += [adapter_cls(entry.routes, **entry.config)]

    if unknowns:
        raise ValueError("Unknown adapter(s): {}".format(", ".join(unknowns)))

    app.extra['adapters'] = adapters
