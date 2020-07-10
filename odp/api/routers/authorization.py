from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from odp.api.admin import get_hydra_admin
from odp.api.db import get_db_session
from odp.api.models.auth import AuthorizationRequest, AccessTokenData, TokenIntrospection
from odp.db.models.user import User
from odp.lib import exceptions as x
from odp.lib.auth import get_token_data
from odp.lib.hydra import HydraAdminClient

router = APIRouter()


@router.post('/introspect', response_model=TokenIntrospection)
async def introspect_token(
        token: str = Form(...),
        scope: str = Form(None),
        hydra: HydraAdminClient = Depends(get_hydra_admin),
        session: Session = Depends(get_db_session),
):
    """ Token introspection endpoint.

    This endpoint conforms to the :rfc:`7662` specification, and is a facade to the
    `ORY Hydra introspection endpoint <https://www.ory.sh/hydra/docs/reference/api/#introspect-oauth2-tokens>`_.

    A valid response will have an :class:`AccessTokenData` dict set on the `ext` property.
    """

    def invalid_token_response(error):
        return TokenIntrospection(active=False, error=error)

    try:
        token_data = TokenIntrospection(**hydra.introspect_token(
            token=token,
            require_scope=scope.split() if scope is not None else None,
        ))
        if not token_data.active:
            return invalid_token_response("Hydra: invalid token")

    except x.HydraAdminError as e:
        raise HTTPException(status_code=e.status_code, detail=e.error_detail) from e

    try:
        # leave this here for debugging
        issue_time = datetime.fromtimestamp(token_data.iat, timezone.utc)
        expiry_time = datetime.fromtimestamp(token_data.exp, timezone.utc)
    except TypeError:
        pass

    user = session.query(User).get(token_data.sub)
    if not user:
        return invalid_token_response(f"User {token_data.sub} not found")
    if not user.active:
        return invalid_token_response(f"User account {token_data.sub} is disabled")

    if token_data.ext is None:
        # if the token was obtained by a client credentials grant,
        # there won't be anything in ext
        scopes = scope.split() if scope is not None else token_data.scope.split()
        token_data.ext, _ = get_token_data(user, scopes)

    elif scope is not None:
        # the token might be valid for multiple scopes, but we must
        # constrain privileges to the requested scopes, if specified
        token_data.ext.access_rights = [
            r for r in token_data.ext.access_rights
            if r.scope_key in scope.split()
        ]

    return token_data


@router.post('/', response_model=AccessTokenData)
async def validate_and_introspect_token(
        auth_request: AuthorizationRequest,
        request: Request,
):
    config = request.app.extra['config']
    try:
        hydra_admin = HydraAdminClient(
            server_url=config.HYDRA_ADMIN_URL,
            verify_tls=config.SERVER_ENV != 'development',
        )
        # this verifies token validity
        token_data = hydra_admin.introspect_token(
            token=auth_request.token,
            require_scope=[auth_request.scope],
        )
    except x.HydraAdminError as e:
        raise HTTPException(status_code=e.status_code, detail=e.error_detail) from e

    access_token = TokenIntrospection(**token_data)
    issue_time = datetime.fromtimestamp(access_token.iat, timezone.utc)
    expiry_time = datetime.fromtimestamp(access_token.exp, timezone.utc)

    access_token_data = AccessTokenData(**access_token.ext.dict())
    assert access_token_data.user_id == access_token.sub

    allow = access_token_data.superuser
    if not allow:
        # the token might be valid for multiple scopes, but we must only consider privileges
        # related to the requested scope
        access_token_data.access_rights = [
            r for r in access_token_data.access_rights
            if r.scope_key == auth_request.scope
        ]
        # filter privileges to include only those indicating that the user has a "super" role
        # (within any institution), or that the user has an applicable role within the given institution
        access_token_data.access_rights = [
            r for r in access_token_data.access_rights
            if r.role_key in auth_request.super_roles or
               (r.role_key in auth_request.institutional_roles and r.institution_key == auth_request.institution)
        ]
        allow = len(access_token_data.access_rights) > 0

    if not allow:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Insufficient privileges")

    return access_token_data
