from dataclasses import dataclass
from typing import Optional, Union, Set, Literal

from fastapi import HTTPException
from fastapi.openapi.models import OAuth2, OAuthFlows, OAuthFlowClientCredentials
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from ory_hydra_client import ApiClient, Configuration
from ory_hydra_client.api.admin_api import AdminApi
from ory_hydra_client.model.o_auth2_token_introspection import OAuth2TokenIntrospection
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY

from odp import ODPScope
from odp.api.models import FlagInstanceModelIn, TagInstanceModelIn
from odp.config import config
from odp.db import Session
from odp.db.models import Flag, Tag
from odp.lib.auth import get_client_permissions, get_user_permissions

_hydra_admin_api = AdminApi(ApiClient(Configuration(config.HYDRA.ADMIN.URL)))
_hydra_public_url = config.HYDRA.PUBLIC.URL


@dataclass
class Authorized:
    client_id: str
    user_id: Optional[str]
    provider_ids: Union[Set[str], Literal['*']]


def _authorize_request(request: Request, required_scope_id: str) -> Authorized:
    auth_header = request.headers.get('Authorization')
    scheme, access_token = get_authorization_scheme_param(auth_header)
    if not auth_header or scheme.lower() != 'bearer':
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    token: OAuth2TokenIntrospection = _hydra_admin_api.introspect_o_auth2_token(
        token=access_token,
        scope=required_scope_id,
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
            provider_ids=client_permissions[required_scope_id],
        )

    # user-initiated API call
    user_permissions = get_user_permissions(token.sub, token.client_id)
    if required_scope_id not in user_permissions:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return Authorized(
        client_id=token.client_id,
        user_id=token.sub,
        provider_ids=user_permissions[required_scope_id],
    )


class BaseAuthorize(SecurityBase):

    def __init__(self):
        # OpenAPI docs / Swagger auth
        self.scheme_name = 'ODP API Authorization'
        self.model = OAuth2(flows=OAuthFlows(clientCredentials=OAuthFlowClientCredentials(
            tokenUrl=f'{_hydra_public_url}/oauth2/token',
            scopes={s.value: s.value for s in ODPScope},
        )))


class Authorize(BaseAuthorize):
    def __init__(self, scope: ODPScope):
        super().__init__()
        self.scope_id = scope.value

    async def __call__(self, request: Request) -> Authorized:
        return _authorize_request(request, self.scope_id)


class FlagAuthorize(BaseAuthorize):
    async def __call__(self, request: Request, flag_instance_in: FlagInstanceModelIn) -> Authorized:
        if not (flag := Session.get(Flag, flag_instance_in.flag_id)):
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid flag id')

        return _authorize_request(request, flag.scope_id)


class UnflagAuthorize(BaseAuthorize):
    async def __call__(self, request: Request, flag_id: str) -> Authorized:
        if not (flag := Session.get(Flag, flag_id)):
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid flag id')

        return _authorize_request(request, flag.scope_id)


class TagAuthorize(BaseAuthorize):
    async def __call__(self, request: Request, tag_instance_in: TagInstanceModelIn) -> Authorized:
        if not (tag := Session.get(Tag, tag_instance_in.tag_id)):
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

        return _authorize_request(request, tag.scope_id)


class UntagAuthorize(BaseAuthorize):
    async def __call__(self, request: Request, tag_id: str) -> Authorized:
        if not (tag := Session.get(Tag, tag_id)):
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

        return _authorize_request(request, tag.scope_id)