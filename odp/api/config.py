from typing import List, Union, Literal

from pydantic import BaseSettings, constr, AnyHttpUrl

from odp.api.models.env import ServerEnv


class Config(BaseSettings):
    SERVER_ENV: ServerEnv
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''
    ALLOW_ORIGINS: List[Union[Literal['*'], AnyHttpUrl]] = []
    ADMIN_API_URL: AnyHttpUrl
    HYDRA_ADMIN_URL: AnyHttpUrl
    CKAN_URL: AnyHttpUrl
