from datetime import datetime, timezone
from typing import Union

from fastapi import APIRouter, Depends, Form
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from odp.api.dependencies.db import get_db_session
from odp.api.dependencies.hydra import get_hydra_admin
from odp.api.models.auth import ValidToken, InvalidToken
from odp.db.models.user import User
from odp.lib import exceptions as x
from odp.lib.auth import get_token_data
from odp.lib.hydra_admin import HydraAdminClient

router = APIRouter()


@router.post('/introspect', response_model=Union[ValidToken, InvalidToken])
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
    try:
        token_data = hydra.introspect_token(
            token=token,
            require_scope=scope.split() if scope is not None else None,
        )
        if not token_data['active']:
            return InvalidToken(error="Hydra: invalid token")

        valid_token = ValidToken(**token_data)

    except x.HydraAdminError as e:
        raise HTTPException(status_code=e.status_code, detail=e.error_detail) from e

    try:
        # leave this here for debugging
        issue_time = datetime.fromtimestamp(valid_token.iat, timezone.utc)
        expiry_time = datetime.fromtimestamp(valid_token.exp, timezone.utc)
    except TypeError:
        pass

    user = session.query(User).get(valid_token.sub)
    if not user:
        return InvalidToken(error=f"User {valid_token.sub} not found")
    if not user.active:
        return InvalidToken(error=f"User account {valid_token.sub} is disabled")

    if valid_token.ext is None:
        # if the token was obtained by a client credentials grant,
        # there won't be anything in ext
        scopes = scope.split() if scope is not None else valid_token.scope.split()
        valid_token.ext, _ = get_token_data(user, scopes)

    elif scope is not None:
        # the token might be valid for multiple scopes, but we must
        # constrain privileges to the requested scopes, if specified
        valid_token.ext.access_rights = [
            r for r in valid_token.ext.access_rights
            if r.scope_key in scope.split()
        ]

    return valid_token
