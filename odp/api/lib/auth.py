from dataclasses import dataclass
from typing import Literal, Optional, Set

from fastapi import HTTPException
from fastapi.openapi.models import OAuth2, OAuthFlowClientCredentials, OAuthFlows
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy import select
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY

from odp import ODPScope
from odp.api.models import TagInstanceModelIn
from odp.config import config
from odp.db import Session
from odp.db.models import Scope, ScopeType, Tag
from odp.lib.auth import get_client_permissions, get_user_permissions
from odp.lib.hydra import HydraAdminAPI, OAuth2TokenIntrospection

hydra_admin_api = HydraAdminAPI(config.HYDRA.ADMIN.URL)
hydra_public_url = config.HYDRA.PUBLIC.URL


@dataclass
class Authorized:
    client_id: str
    user_id: Optional[str]
    collection_ids: Set[str] | Literal['*']


def _authorize_request(request: Request, required_scope_id: str) -> Authorized:
    auth_header = request.headers.get('Authorization')
    scheme, access_token = get_authorization_scheme_param(auth_header)
    if not auth_header or scheme.lower() != 'bearer':
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    token: OAuth2TokenIntrospection = hydra_admin_api.introspect_token(
        access_token, [required_scope_id],
    )
    if not token.active:
        raise HTTPException(HTTP_403_FORBIDDEN)

    # if sub == client_id it's an API call from a client,
    # using a client credentials grant
    if token.sub == token.client_id:
        client_permissions = get_client_permissions(token.client_id)
        if required_scope_id not in client_permissions:
            raise HTTPException(HTTP_403_FORBIDDEN)

        return Authorized(
            client_id=token.client_id,
            user_id=None,
            collection_ids=client_permissions[required_scope_id],
        )

    # user-initiated API call
    user_permissions = get_user_permissions(token.sub, token.client_id)
    if required_scope_id not in user_permissions:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return Authorized(
        client_id=token.client_id,
        user_id=token.sub,
        collection_ids=user_permissions[required_scope_id],
    )


class BaseAuthorize(SecurityBase):

    def __init__(self):
        # OpenAPI docs / Swagger auth
        self.scheme_name = 'ODP API Authorization'
        self.model = OAuth2(flows=OAuthFlows(clientCredentials=OAuthFlowClientCredentials(
            tokenUrl=f'{hydra_public_url}/oauth2/token',
            scopes={s.value: s.value for s in ODPScope},
        )))


class Authorize(BaseAuthorize):
    def __init__(self, scope: ODPScope):
        super().__init__()
        self.scope_id = scope.value

    async def __call__(self, request: Request) -> Authorized:
        return _authorize_request(request, self.scope_id)


class TagAuthorize(BaseAuthorize):
    async def __call__(self, request: Request, tag_instance_in: TagInstanceModelIn) -> Authorized:
        if not (tag := Session.execute(
                select(Tag).
                where(Tag.id == tag_instance_in.tag_id)
        ).scalar_one_or_none()):
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

        return _authorize_request(request, tag.scope_id)


class UntagAuthorize(BaseAuthorize):
    async def __call__(self, request: Request, tag_id: str) -> Authorized:
        if not (tag := Session.execute(
                select(Tag).
                where(Tag.id == tag_id)
        ).scalar_one_or_none()):
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

        return _authorize_request(request, tag.scope_id)


def select_scopes(
        scope_ids: list[str],
        scope_types: list[ScopeType] = None,
) -> list[Scope]:
    """Select Scope objects given a list of ids,
    optionally constrained to the given types."""
    scopes = []
    invalid_ids = []
    for scope_id in scope_ids:
        stmt = select(Scope).where(Scope.id == scope_id)
        if scope_types is not None:
            stmt = stmt.where(Scope.type.in_(scope_types))

        if scope := Session.execute(stmt).scalar_one_or_none():
            scopes += [scope]
        else:
            invalid_ids += [scope_id]

    if invalid_ids:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, f'Scope(s) not allowed: {", ".join(invalid_ids)}')

    return scopes
