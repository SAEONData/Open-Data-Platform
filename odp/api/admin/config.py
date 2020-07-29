from pydantic import AnyHttpUrl

from odp.api.config import APIConfig


class AdminAPIConfig(APIConfig):
    """ Config specific to the admin API """
    HYDRA_ADMIN_URL: AnyHttpUrl
