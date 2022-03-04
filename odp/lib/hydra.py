from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from ory_hydra_client import ApiClient, Configuration
from ory_hydra_client.api.admin_api import AdminApi, OAuth2Client
from ory_hydra_client.exceptions import ApiException
from ory_hydra_client.model.o_auth2_token_introspection import OAuth2TokenIntrospection
from ory_hydra_client.model.string_slice_pipe_delimiter import StringSlicePipeDelimiter as StringArray


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


@dataclass
class HydraClient:
    id: str
    name: str
    scope_ids: list[str]
    grant_types: list[GrantType]
    response_types: list[ResponseType]
    redirect_uris: list[str]
    post_logout_redirect_uris: list[str]
    token_endpoint_auth_method: TokenEndpointAuthMethod
    allowed_cors_origins: list[str]


class HydraAdminAPI:
    """A wrapper for the Hydra SDK's admin API."""

    def __init__(self, hydra_admin_url: str) -> None:
        self._api = AdminApi(ApiClient(Configuration(hydra_admin_url)))

    def introspect_token(
            self,
            access_or_refresh_token: str,
            required_scope_ids: list[str] = None,
    ) -> OAuth2TokenIntrospection:
        kwargs = dict(token=access_or_refresh_token)
        if required_scope_ids is not None:
            kwargs |= dict(scope=' '.join(required_scope_ids))

        return self._api.introspect_o_auth2_token(**kwargs)

    def get_client(self, id: str) -> HydraClient:
        oauth2_client = self._api.get_o_auth2_client(id=id)
        try:
            post_logout_redirect_uris = oauth2_client.post_logout_redirect_uris.value
        except AttributeError:
            # handle missing post_logout_redirect_uris on returned client credentials clients
            post_logout_redirect_uris = []

        return HydraClient(
            id=oauth2_client.client_id,
            name=oauth2_client.client_name,
            scope_ids=oauth2_client.scope.split(),
            grant_types=oauth2_client.grant_types.value,
            response_types=oauth2_client.response_types.value,
            redirect_uris=oauth2_client.redirect_uris.value,
            post_logout_redirect_uris=post_logout_redirect_uris,
            token_endpoint_auth_method=oauth2_client.token_endpoint_auth_method,
            allowed_cors_origins=oauth2_client.allowed_cors_origins.value,
        )

    def create_or_update_client(
            self,
            id: str,
            *,
            name: str,
            secret: str,
            scope_ids: Iterable[str],
            grant_types: Iterable[GrantType],
            response_types: Iterable[ResponseType] = (),
            redirect_uris: Iterable[str] = (),
            post_logout_redirect_uris: Iterable[str] = (),
            token_endpoint_auth_method: TokenEndpointAuthMethod = TokenEndpointAuthMethod.CLIENT_SECRET_BASIC,
            allowed_cors_origins: Iterable[str] = (),
    ) -> None:
        oauth2_client = OAuth2Client(
            client_id=id,
            client_name=name,
            client_secret=secret,
            scope=' '.join(scope_ids),
            grant_types=StringArray(list(grant_types)),
            response_types=StringArray(list(response_types)),
            redirect_uris=StringArray(list(redirect_uris)),
            post_logout_redirect_uris=StringArray(list(post_logout_redirect_uris)),
            token_endpoint_auth_method=token_endpoint_auth_method,
            allowed_cors_origins=StringArray(list(allowed_cors_origins)),
            contacts=StringArray([]),
        )
        try:
            self._api.create_o_auth2_client(body=oauth2_client)
        except ApiException as e:
            if e.status == 409:
                self._api.update_o_auth2_client(id=id, body=oauth2_client)
            else:
                raise  # todo: raise our own exception class here
