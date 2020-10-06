from pydantic import AnyHttpUrl

from odp.config import BaseConfig


class DataciteConfig(BaseConfig):
    class Config:
        env_prefix = 'DATACITE_'

    # URL of the DataCite REST API
    # Note: DataCite's test API should be used in non-production environments
    API_URL: AnyHttpUrl

    USERNAME: str    # DataCite account username
    PASSWORD: str    # DataCite account password
    DOI_PREFIX: str  # the DOI prefix associated with our DataCite account
    DOI_LANDING_PAGE_BASE_URL: AnyHttpUrl  # base URL for DOI back-links