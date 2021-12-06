from pydantic import AnyHttpUrl

from odp.config import BaseConfig


class DatacitePublishConfig(BaseConfig):
    class Config:
        env_prefix = 'DATACITE_PUBLISH_'

    BATCH_SIZE: int   # maximum number of records to sync in a publishing run
    MAX_RETRIES: int  # number of times to retry syncing a given record after failure


class DataciteConfig(BaseConfig):
    class Config:
        env_prefix = 'DATACITE_'

    # URL of the DataCite REST API
    # Note: DataCite's test API should be used in non-production environments
    API_URL: AnyHttpUrl

    USERNAME: str    # DataCite account username
    PASSWORD: str    # DataCite account password
    DOI_LANDING_PAGE_BASE_URL: AnyHttpUrl  # base URL for DOI back-links

    _subconfig = {
        'PUBLISH': DatacitePublishConfig,
    }
