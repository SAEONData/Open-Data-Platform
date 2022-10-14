from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api.lib.auth import Authorize, Authorized
from odp.api.models import TokenModel, TokenModelIn
from odp.db import Session
from odp.db.models import OAuth2Token

router = APIRouter()


@router.get(
    '/{user_id}',
    response_model=TokenModel,
)
async def get_token(
        user_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.TOKEN_READ)),
):
    if auth.user_id is not None and auth.user_id != user_id:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (token := Session.get(OAuth2Token, (auth.client_id, user_id))):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return TokenModel(
        token_type=token.token_type,
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        id_token=token.id_token,
        expires_at=token.expires_at,
    )


@router.put(
    '/{user_id}',
)
async def set_token(
        user_id: str,
        token_in: TokenModelIn,
        auth: Authorized = Depends(Authorize(ODPScope.TOKEN_WRITE)),
):
    if auth.user_id is not None and auth.user_id != user_id:
        raise HTTPException(HTTP_403_FORBIDDEN)

    token = (Session.get(OAuth2Token, (auth.client_id, user_id)) or
             OAuth2Token(client_id=auth.client_id, user_id=user_id))

    token.token_type = token_in.token_type
    token.access_token = token_in.access_token
    token.refresh_token = token_in.refresh_token
    token.id_token = token_in.id_token
    token.expires_at = token_in.expires_at
    token.save()
