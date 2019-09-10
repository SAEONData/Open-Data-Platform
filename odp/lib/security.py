from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from typing import List

from hydra import HydraAdminClient, HydraAdminError


class HydraAuth(HTTPBearer):

    def __init__(self, required_scopes: List[str]):
        super().__init__(auto_error=True)
        self.required_scopes = required_scopes

    async def __call__(self, request: Request) -> str:
        """
        Validate and return the access token that was supplied in the Authorization header.
        :return: str
        """
        config = request.app.extra['config'].security
        validate_token = not config.no_access_token_validation

        auth_credentials = await super().__call__(request)
        access_token = auth_credentials.credentials

        if validate_token:
            try:
                hydra_admin = HydraAdminClient(
                    server_url=config.hydra_admin_url,
                    verify_tls=not config.hydra_dev_server,
                )
                hydra_admin.introspect_token(access_token, self.required_scopes, [config.oauth2_audience])
            except HydraAdminError as e:
                raise HTTPException(status_code=e.status_code, detail=e.error_detail)

        return access_token
