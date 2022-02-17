from ory_hydra_client import ApiClient, Configuration
from ory_hydra_client.api.admin_api import AdminApi, OAuth2Client
from ory_hydra_client.exceptions import ApiException
from ory_hydra_client.model.o_auth2_token_introspection import OAuth2TokenIntrospection
from ory_hydra_client.model.string_slice_pipe_delimiter import StringSlicePipeDelimiter as StringArray


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

    def create_or_update_client_credentials_client(
            self,
            client_id: str,
            client_name: str,
            client_secret: str,
            allowed_scope_ids: list[str],
    ) -> None:
        oauth2_client = OAuth2Client(
            client_id=client_id,
            client_name=client_name,
            client_secret=client_secret,
            scope=' '.join(allowed_scope_ids),
            grant_types=StringArray(['client_credentials']),
            response_types=StringArray([]),
            redirect_uris=StringArray([]),
            contacts=StringArray([]),
        )
        try:
            self._api.create_o_auth2_client(body=oauth2_client)
        except ApiException as e:
            if e.status == 409:
                self._api.update_o_auth2_client(id=client_id, body=oauth2_client)
            else:
                raise  # todo: raise our own exception class here
