from fastapi import APIRouter, Depends

from odp.api.lib.auth import Authorize, Authorized
from odp.api.models import AccessTokenModel
from odp.lib.auth import get_client_permissions, get_user_permissions
from odplib.const import ODPScope

router = APIRouter()


@router.get(
    '/',
    response_model=AccessTokenModel,
)
async def get_access_token_data(
        auth: Authorized = Depends(Authorize(ODPScope.TOKEN_READ)),
):
    if auth.user_id is not None:
        permissions = get_user_permissions(auth.user_id, auth.client_id)
    else:
        permissions = get_client_permissions(auth.client_id)

    return AccessTokenModel(
        client_id=auth.client_id,
        user_id=auth.user_id,
        permissions=permissions,
    )
