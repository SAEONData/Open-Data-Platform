from enum import Enum


class GrantType(str, Enum):
    """Grant types supported by Hydra. 'implicit' is
    excluded here, as it is insecure."""
    AUTHORIZATION_CODE = 'authorization_code'
    CLIENT_CREDENTIALS = 'client_credentials'
    REFRESH_TOKEN = 'refresh_token'


class ResponseType(str, Enum):
    """Response types supported by Hydra."""
    CODE = 'code'
    CODE_IDTOKEN = 'code id_token'
    IDTOKEN = 'id_token'
    TOKEN = 'token'
    TOKEN_IDTOKEN = 'token id_token'
    TOKEN_IDTOKEN_CODE = 'token id_token code'


class HydraScope(str, Enum):
    """Standard scopes implemented by Hydra. 'offline' is
    excluded here, as it is just an alias for 'offline_access'."""
    OPENID = 'openid'
    OFFLINE_ACCESS = 'offline_access'


class StandardScope(str, Enum):
    OPENID = 'openid'
    OFFLINE = 'offline'
    OFFLINE_ACCESS = 'offline_access'
    PROFILE = 'profile'
    EMAIL = 'email'
    ADDRESS = 'address'
    PHONE = 'phone'


class TokenEndpointAuthMethod(str, Enum):
    CLIENT_SECRET_BASIC = 'client_secret_basic'
    CLIENT_SECRET_POST = 'client_secret_post'
