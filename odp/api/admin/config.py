from pydantic import BaseSettings, AnyHttpUrl

from odp.api.models.env import ServerEnv


class Config(BaseSettings):
    """
    Application config, populated from the environment.
    """
    SERVER_ENV: ServerEnv
    HYDRA_ADMIN_URL: AnyHttpUrl
