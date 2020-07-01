from pydantic import BaseSettings, AnyHttpUrl, constr

from odp.api.models.env import ServerEnv


class Config(BaseSettings):
    """
    Application config, populated from the environment.
    """
    SERVER_ENV: ServerEnv
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''
    HYDRA_ADMIN_URL: AnyHttpUrl
