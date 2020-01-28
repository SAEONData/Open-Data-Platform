from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.requests import Request

from hydra import HydraAdminClient, HydraAdminError
from odpaccounts.authorization.models import AccessToken, AuthorizedUser

from ..models.authorization import TokenIn

router = APIRouter()


@router.post('/', response_model=AuthorizedUser)
async def authorize(
        token_in: TokenIn,
        request: Request,
):
    config = request.app.extra['config']
    try:
        hydra_admin = HydraAdminClient(
            server_url=config.HYDRA_ADMIN_URL,
            verify_tls=config.SERVER_ENV != 'development',
        )
        access_token = AccessToken(**hydra_admin.introspect_token(
            token_in.token,
            token_in.require_scope,
            token_in.require_audience,
        ))
        authorized_user = AuthorizedUser(**access_token.ext.dict())
        assert authorized_user.user_id == access_token.sub
        return authorized_user

    except HydraAdminError as e:
        raise HTTPException(status_code=e.status_code, detail=e.error_detail)
