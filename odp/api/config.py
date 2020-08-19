from typing import List, Union, Literal

from pydantic import BaseSettings, constr, AnyHttpUrl, validator, PostgresDsn

from odp.api.models import KEY_REGEX
from odp.api.models.env import ServerEnv


class Config(BaseSettings):
    """ Environment variables used by the ODP admin and public APIs """

    # deployment environment
    SERVER_ENV: ServerEnv

    # (optional) URL path prefix at which the API is mounted, e.g. `/api`
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''

    # (optional) JSON-encoded list of allowed CORS origins; `["*"]` to allow any origin
    ALLOW_ORIGINS: List[Union[Literal['*'], AnyHttpUrl]] = []

    # URL of the ODP accounts database
    DATABASE_URL: PostgresDsn

    # institution key of the institution that owns the platform
    ADMIN_INSTITUTION: constr(regex=KEY_REGEX)

    # URL of the ODP admin API
    ADMIN_API_URL: AnyHttpUrl

    # URL of the Hydra admin API
    HYDRA_ADMIN_URL: AnyHttpUrl

    # URL of the CKAN metadata management server
    CKAN_URL: AnyHttpUrl

    # URL of the Elasticsearch metadata discovery instance; must include port
    ES_URL: AnyHttpUrl

    # JSON-encoded list of Elasticsearch indices to use for search queries
    ES_INDICES: List[str]

    @validator('ES_URL')
    def check_port(cls, v):
        if not v.port:
            raise ValueError("Port must be specified in the Elasticsearch URL")
        return v
