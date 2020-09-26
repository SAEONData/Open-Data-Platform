from pydantic import AnyHttpUrl

from odp.config import BaseConfig


class CatalogueConfig(BaseConfig):
    class Config:
        env_prefix = 'CATALOGUE_'

    # base URL for metadata landing pages (to which DOI links ultimately resolve)
    METADATA_LANDING_PAGE_BASE_URL: AnyHttpUrl
