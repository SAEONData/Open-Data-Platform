from ory_hydra_client import ApiClient, Configuration
from ory_hydra_client.api.admin_api import AdminApi
from ory_hydra_client.model.o_auth2_token_introspection import OAuth2TokenIntrospection


class HydraAdminAPI:
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
