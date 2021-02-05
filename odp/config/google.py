from pydantic import AnyHttpUrl

from odp.config import BaseConfig
from odp.config.mixins import OAuth2ClientConfigMixin


class GoogleConfig(BaseConfig, OAuth2ClientConfigMixin):
    class Config:
        env_prefix = 'GOOGLE_'

    AUTH_URI: AnyHttpUrl  # Google auth endpoint
    TOKEN_URI: AnyHttpUrl  # Google token endpoint
    OPENID_URI: AnyHttpUrl  # Google OpenID configuration
