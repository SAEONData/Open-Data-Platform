from typing import List

from pydantic import validator, AnyHttpUrl

from odp.config import BaseConfig


class ElasticConfig(BaseConfig):
    class Config:
        env_prefix = 'ELASTIC_'

    URL: AnyHttpUrl     # URL of the Elasticsearch instance; must include port
    INDICES: List[str]  # JSON-encoded list of indices to use for search queries

    @validator('URL')
    def check_port(cls, v):
        if not v.port:
            raise ValueError("Elasticsearch URL must include port")
        return v
