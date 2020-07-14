from typing import NamedTuple

import requests
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE, HTTP_403_FORBIDDEN

from odp.api.models.auth import AccessTokenData, TokenIntrospection, Role
from odp.lib.auth import check_access


class AuthData(NamedTuple):
    access_token: str
    access_token_data: AccessTokenData


class Authorizer(HTTPBearer):
    """
    Dependency class which authorizes the current request.
    """

    def __init__(self, *allowed_roles: Role):
        """
        Constructor.

        :param allowed_roles: the role(s) that are allowed access to the API function
        """
        super().__init__(auto_error=True)
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, institution_key: str = None) -> AuthData:
        """
        Validate the access token that was supplied in the Authorization header,
        and return the token and associated access rights on success.

        :param institution_key: the institution that owns the resource(s) being requested, if applicable
        :return: AuthData(access_token, access_token_data)
        :raise HTTPException: if the token is invalid or the user has insufficient privileges
        """
        http_auth = await super().__call__(request)
        access_token = http_auth.credentials
        config = request.app.extra['config']
        router_scope = request.state.config.OAUTH2_SCOPE
        development_env = config.SERVER_ENV == 'development'
        try:
            r = requests.post(
                config.ADMIN_API_URL + '/auth/introspect',
                data={
                    'token': access_token,
                    'scope': router_scope,
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                },
                verify=not development_env,
                timeout=None if development_env else 5.0,
            )
            r.raise_for_status()
            token_data = TokenIntrospection(**r.json())

            allow_access = check_access(
                access_token_data := token_data.ext,
                require_institution=institution_key,
                require_scope=router_scope,
                require_role=self.allowed_roles,
            )

            if not allow_access:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Insufficient privileges",
                )

            return AuthData(access_token, access_token_data)

        except requests.HTTPError as e:
            try:
                detail = e.response.json()
            except ValueError:
                detail = e.response.reason
            raise HTTPException(status_code=e.response.status_code, detail=detail) from e

        except requests.RequestException as e:
            raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e
