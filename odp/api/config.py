from typing import List, Union, Literal

from pydantic import BaseSettings, constr, AnyHttpUrl, validator

from odp.api.models.env import ServerEnv


class Config(BaseSettings):
    SERVER_ENV: ServerEnv
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''
    ALLOW_ORIGINS: List[Union[Literal['*'], AnyHttpUrl]] = []
    ADMIN_API_URL: AnyHttpUrl
    HYDRA_ADMIN_URL: AnyHttpUrl
    CKAN_URL: AnyHttpUrl
    ES_URL: AnyHttpUrl
    ES_INDICES: List[str]

    @validator('ES_URL')
    def check_port(cls, v):
        if not v.port:
            raise ValueError("Port must be specified in the Elasticsearch URL")
        return v
