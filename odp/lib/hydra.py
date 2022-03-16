from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional

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

    @classmethod
    def from_oauth2_client(cls, oauth2_client: OAuth2Client) -> HydraClient:
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


class HydraAdminAPI:
    """A wrapper for the Hydra SDK's admin API."""

    def __init__(self, hydra_admin_url: str) -> None:
        self._api = AdminApi(ApiClient(Configuration(hydra_admin_url)))

    def introspect_token(
            self,
            access_or_refresh_token: str,
            required_scope_ids: list[str] = None,
    ) -> OAuth2TokenIntrospection:
        """Check access/refresh token validity and return detailed
        token information."""
        kwargs = dict(token=access_or_refresh_token)
        if required_scope_ids is not None:
            kwargs |= dict(scope=' '.join(required_scope_ids))

        return self._api.introspect_o_auth2_token(**kwargs)

    def list_clients(self) -> list[HydraClient]:
        """Return a list of all OAuth2 clients from Hydra."""
        oauth2_clients = self._api.list_o_auth2_clients()
        return [HydraClient.from_oauth2_client(oauth2_client)
                for oauth2_client in oauth2_clients]

    def get_client(self, id: str) -> HydraClient:
        """Get an OAuth2 client configuration from Hydra."""
        oauth2_client = self._api.get_o_auth2_client(id=id)
        return HydraClient.from_oauth2_client(oauth2_client)

    def create_or_update_client(
            self,
            id: str,
            *,
            name: str,
            secret: Optional[str],
            scope_ids: Iterable[str],
            grant_types: Iterable[GrantType],
            response_types: Iterable[ResponseType] = (),
            redirect_uris: Iterable[str] = (),
            post_logout_redirect_uris: Iterable[str] = (),
            token_endpoint_auth_method: TokenEndpointAuthMethod = TokenEndpointAuthMethod.CLIENT_SECRET_BASIC,
            allowed_cors_origins: Iterable[str] = (),
    ) -> None:
        """Create or update an OAuth2 client configuration on Hydra.

        On update, pass `secret=None` to leave the client secret unchanged.
        """
        kwargs = dict(
            client_id=id,
            client_name=name,
            scope=' '.join(scope_ids),
            grant_types=StringArray(list(grant_types)),
            response_types=StringArray(list(response_types)),
            redirect_uris=StringArray(list(redirect_uris)),
            post_logout_redirect_uris=StringArray(list(post_logout_redirect_uris)),
            token_endpoint_auth_method=token_endpoint_auth_method,
            allowed_cors_origins=StringArray(list(allowed_cors_origins)),
            contacts=StringArray([]),
        )
        if secret is not None:
            kwargs |= dict(client_secret=secret)

        oauth2_client = OAuth2Client(**kwargs)
        try:
            self._api.create_o_auth2_client(oauth2_client)
        except ApiException as e:
            if e.status == 409:
                self._api.update_o_auth2_client(id, oauth2_client)
            else:
                raise  # todo: raise our own exception class here

    def delete_client(self, id: str) -> None:
        """Delete an OAuth2 client configuration from Hydra."""
        self._api.delete_o_auth2_client(id=id)
