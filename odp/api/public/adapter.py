from fastapi import FastAPI
from pydantic import BaseSettings


class ODPAPIAdapterConfig(BaseSettings):
    pass


class ODPAPIAdapter:
    def __init__(self, app: FastAPI, config: ODPAPIAdapterConfig):
        self.app = app
        self.config = config
        self.app_config = self.app.extra['config']
