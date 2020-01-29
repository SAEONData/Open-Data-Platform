from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.requests import Request

from hydra import HydraAdminClient, HydraAdminError
from odpaccounts.auth.models import AccessToken, AccessRights

from ..models.authorization import TokenIn

router = APIRouter()


@router.post('/', response_model=AccessRights)
async def validate_and_introspect_token(
        token_in: TokenIn,
        request: Request,
):
    config = request.app.extra['config']
    try:
        hydra_admin = HydraAdminClient(
            server_url=config.HYDRA_ADMIN_URL,
            verify_tls=config.SERVER_ENV != 'development',
        )
        token_data = hydra_admin.introspect_token(**token_in.dict())
        access_token = AccessToken(**token_data)
        access_rights = AccessRights(**access_token.ext.dict())
        assert access_rights.user_id == access_token.sub
        return access_rights

    except HydraAdminError as e:
        raise HTTPException(status_code=e.status_code, detail=e.error_detail) from e
