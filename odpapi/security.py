from typing import NamedTuple

from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from starlette.requests import Request
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE
import requests

from odpaccounts.auth.models import AccessRights


class AuthData(NamedTuple):
    access_token: str
    access_rights: AccessRights


class Authorizer(HTTPBearer):
    """
    Dependency class which authorizes the current request.
    """
    async def __call__(self, request: Request) -> AuthData:
        """
        Validate the access token that was supplied in the Authorization header,
        and return the token and associated access rights.
        :return: tuple(access_token, access_rights)
        """
        config = request.app.extra['config']
        validate_token = not config.NO_AUTH

        auth_credentials = await super().__call__(request)

        access_token = auth_credentials.credentials
        access_rights = None

        if validate_token:
            try:
                r = requests.post(config.ACCOUNTS_API_URL + '/authorization/',
                                  json={
                                      'token': access_token,
                                      'require_scope': [request.state.config.OAUTH2_SCOPE],
                                      'require_audience': [config.OAUTH2_AUDIENCE],
                                  },
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Accept': 'application/json',
                                  },
                                  verify=config.SERVER_ENV != 'development',
                                  timeout=5.0 if config.SERVER_ENV != 'development' else 300,
                                  )
                r.raise_for_status()
                access_rights = AccessRights(**r.json())

            except requests.HTTPError as e:
                try:
                    detail = e.response.json()
                except ValueError:
                    detail = e.response.reason
                raise HTTPException(status_code=e.response.status_code, detail=detail) from e

            except requests.RequestException as e:
                raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e

        return AuthData(access_token, access_rights)
