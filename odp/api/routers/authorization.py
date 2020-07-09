from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from odp.api.models.auth import AuthorizationRequest, AccessToken, AccessInfo
from odp.lib import exceptions as x
from odp.lib.hydra import HydraAdminClient

router = APIRouter()


@router.post('/', response_model=AccessInfo)
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

    access_token = AccessToken(**token_data)
    issue_time = datetime.fromtimestamp(access_token.iat, timezone.utc)
    expiry_time = datetime.fromtimestamp(access_token.exp, timezone.utc)

    access_info = AccessInfo(**access_token.ext.dict())
    assert access_info.user_id == access_token.sub

    allow = access_info.superuser
    if not allow:
        # the token might be valid for multiple scopes, but we must only consider privileges
        # related to the requested scope
        access_info.access_rights = [r for r in access_info.access_rights if r.scope_key == auth_request.scope]
        # filter privileges to include only those indicating that the user has a "super" role
        # (within any institution), or that the user has an applicable role within the given institution
        access_info.access_rights = [r for r in access_info.access_rights if r.role_key in auth_request.super_roles
                                     or (r.role_key in auth_request.institutional_roles and r.institution_key == auth_request.institution)]
        allow = len(access_info.access_rights) > 0

    if not allow:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Insufficient privileges")

    return access_info
