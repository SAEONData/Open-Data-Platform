from typing import NamedTuple

import requests
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE, HTTP_403_FORBIDDEN

from odp.api.models.auth import AccessTokenData, ValidToken, Role, Scope
from odp.lib.auth import check_access


class AuthData(NamedTuple):
    access_token: str
    access_token_data: AccessTokenData


class Authorizer(HTTPBearer):
    """ Dependency class which authorizes the current request. """

    def __init__(self, scope: Scope, *allowed_roles: Role, institution_key: str = None):
        """ Constructor.

        :param scope: the scope required for accessing the API function
        :param allowed_roles: the role(s) that are allowed access to the API function
        :param institution_key: if specified, the API function may only be accessed by
            members of this institution (or the admin institution)
        """
        super().__init__(auto_error=True)
        self.scope = scope
        self.allowed_roles = allowed_roles
        self.institution_key = institution_key

    async def __call__(self, request: Request, institution_key: str = None) -> AuthData:
        """ Validate the access token that was supplied in the Authorization header,
        and return the token and associated access rights on success.

        :param institution_key: the institution that owns the resource(s) being requested, if applicable
        :return: AuthData(access_token, access_token_data)
        :raise HTTPException: if the token is invalid or the user has insufficient privileges
        """
        http_auth = await super().__call__(request)
        access_token = http_auth.credentials
        config = request.app.extra['config']
        development_env = config.SERVER_ENV == 'development'
        try:
            r = requests.post(
                config.ADMIN_API_URL + '/auth/introspect',
                data={
                    'token': access_token,
                    'scope': self.scope.value,
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                },
                verify=not development_env,
                timeout=None if development_env else 5.0,
            )
            r.raise_for_status()
            token_data = r.json()
            if not token_data['active']:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=token_data['error'],
                )

            valid_token = ValidToken(**token_data)
            allow_access = check_access(
                access_token_data := valid_token.ext,
                require_institution=self.institution_key or institution_key,
                require_scope=self.scope,
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
                detail = e.response.text
            raise HTTPException(status_code=e.response.status_code, detail=detail) from e

        except requests.RequestException as e:
            raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e
