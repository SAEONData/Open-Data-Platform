from pydantic import AnyHttpUrl

from odp.config import BaseConfig


class HydraPublicConfig(BaseConfig):
    class Config:
        env_prefix = 'HYDRA_PUBLIC_'

    URL: AnyHttpUrl  # URL of the Hydra public API (OAuth2/OIDC endpoints)


class HydraAdminConfig(BaseConfig):
    class Config:
        env_prefix = 'HYDRA_ADMIN_'

    URL: AnyHttpUrl  # URL of the Hydra admin API


class HydraConfig(BaseConfig):
    _subconfig = {
        'PUBLIC': HydraPublicConfig,
        'ADMIN': HydraAdminConfig,
    }
