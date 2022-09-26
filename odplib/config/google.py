from pydantic import AnyHttpUrl

from odplib.config import BaseConfig
from odplib.config.mixins import OAuth2ClientConfigMixin


class GoogleConfig(BaseConfig, OAuth2ClientConfigMixin):
    class Config:
        env_prefix = 'GOOGLE_'

    AUTH_URI: AnyHttpUrl  # Google auth endpoint
    TOKEN_URI: AnyHttpUrl  # Google token endpoint
    OPENID_URI: AnyHttpUrl  # Google OpenID configuration

    # enable/disable login via Google:
    # Google only allows redirects to public URLs or to localhost,
    # so it should be disabled, for example, on the dev platform
    ENABLE: bool
