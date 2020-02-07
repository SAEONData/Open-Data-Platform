from typing import NamedTuple

from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from starlette.requests import Request
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE
import requests

from odpaccounts.auth.models import AccessInfo


class AuthData(NamedTuple):
    access_token: str
    access_info: AccessInfo


class Authorizer(HTTPBearer):
    """
    Dependency class which authorizes the current request.
    """
    def __init__(self, read_only: bool = False, admin_only: bool = False):
        """
        Constructor.

        :param read_only: indicates whether the route being requested is read-only
        :param admin_only: indicates whether the route being requested requires an admin role
        """
        super().__init__(auto_error=True)
        self.read_only = read_only
        self.admin_only = admin_only

    async def __call__(self, request: Request, institution_key: str = None) -> AuthData:
        """
        Validate the access token that was supplied in the Authorization header,
        and return the token and associated access rights on success.

        :param institution_key: the institution that owns the resource(s) being requested, if applicable
        :return: tuple(access_token, access_info)
        :raises HTTPException: if the token is invalid or the user has insufficient privileges
        """
        config = request.app.extra['config']

        http_auth = await super().__call__(request)
        access_token = http_auth.credentials

        if config.NO_AUTH:
            access_info = AccessInfo(
                superuser=True,
                user_id='',
                access_rights=[],
            )
        else:
            try:
                if self.admin_only:
                    roles = []
                elif self.read_only:
                    roles = request.state.config.READONLY_ROLES + request.state.config.READWRITE_ROLES
                else:
                    roles = request.state.config.READWRITE_ROLES

                if institution_key:
                    institutional_roles = roles
                    super_roles = request.state.config.ADMIN_ROLES
                else:
                    institutional_roles = []
                    super_roles = request.state.config.ADMIN_ROLES + roles

                r = requests.post(config.ACCOUNTS_API_URL + '/authorization/',
                                  json={
                                      'token': access_token,
                                      'audience': config.OAUTH2_AUDIENCE,
                                      'scope': request.state.config.OAUTH2_SCOPE,
                                      'institution': institution_key,
                                      'institutional_roles': institutional_roles,
                                      'super_roles': super_roles,
                                  },
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Accept': 'application/json',
                                  },
                                  verify=config.SERVER_ENV != 'development',
                                  timeout=5.0 if config.SERVER_ENV != 'development' else 300,
                                  )
                r.raise_for_status()
                access_info = AccessInfo(**r.json())

            except requests.HTTPError as e:
                try:
                    detail = e.response.json()
                except ValueError:
                    detail = e.response.reason
                raise HTTPException(status_code=e.response.status_code, detail=detail) from e

            except requests.RequestException as e:
                raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e

        return AuthData(access_token, access_info)
