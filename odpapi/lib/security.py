from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
import requests
from typing import List


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
        introspect_url = config.hydra_admin_url + '/oauth2/introspect'
        required_audience = config.required_audience
        required_scopes = ' '.join(self.required_scopes)
        insecure_http = config.hydra_insecure_http

        auth_credentials = await super().__call__(request)
        access_token = auth_credentials.credentials

        r = requests.post(introspect_url,
                          verify=not insecure_http,
                          data={
                              'token': access_token,
                              'scope': required_scopes,
                          })
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not validate access token")

        token_info = r.json()
        if not token_info['active'] or required_audience not in token_info['aud']:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid access token")

        return access_token
