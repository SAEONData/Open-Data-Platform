from typing import List

from pydantic import BaseSettings, validator
from pydantic.networks import AnyHttpUrl


class CatalogueConfig(BaseSettings):
    # URL of the Elasticsearch metadata discovery instance; must include port
    ES_URL: AnyHttpUrl

    # JSON-encoded list of Elasticsearch indices to use for search queries
    ES_INDICES: List[str]

    # base URL for metadata landing pages (to which DOI links ultimately resolve)
    METADATA_LANDING_PAGE_BASE_URL: AnyHttpUrl

    @validator('ES_URL')
    def check_port(cls, v):
        if not v.port:
            raise ValueError("Port must be specified in the Elasticsearch URL")
        return v

    class Config:
        env_prefix = 'CATALOGUE.'
