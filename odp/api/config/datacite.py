from pydantic import BaseSettings
from pydantic.networks import AnyHttpUrl


class DataCiteConfig(BaseSettings):
    # URL of the DataCite REST API
    API_URL: AnyHttpUrl

    # DataCite REST API test URL
    API_TEST_URL: AnyHttpUrl

    # DOI prefix for metadata published to DataCite
    DOI_PREFIX: str

    # DataCite account username
    USERNAME: str

    # DataCite account password
    PASSWORD: str

    class Config:
        env_prefix = 'DATACITE.'
