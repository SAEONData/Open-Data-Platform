from pydantic import BaseSettings, constr, AnyHttpUrl

from odp.api.models.env import ServerEnv


class APIConfig(BaseSettings):
    """ Config common to all API instances """
    SERVER_ENV: ServerEnv
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''
    ADMIN_API_URL: AnyHttpUrl
