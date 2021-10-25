from dataclasses import dataclass
from typing import Union, Set, Literal

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from ory_hydra_client import ApiClient, Configuration
from ory_hydra_client.api.admin_api import AdminApi, OAuth2TokenIntrospection
from starlette.status import HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY

from odp import ODPScope
from odp.config import config
from odp.lib.auth import get_client_auth, get_user_auth


@dataclass
class Pager:
    sort: str
    skip: int
    limit: int


class Paging:
    def __init__(self, sort_enum):
        self.sort_keys = [e.value for e in sort_enum]

    async def __call__(self, sort: str = None, skip: int = 0, limit: int = 100) -> Pager:
        if sort and sort not in self.sort_keys:
            raise HTTPException(
                HTTP_422_UNPROCESSABLE_ENTITY,
                f'Sort key must be one of {self.sort_keys}',
            )
        sort = sort or self.sort_keys[0]
        return Pager(sort=sort, skip=skip, limit=limit)


@dataclass
class Authorized:
    provider_ids: Union[Set[str], Literal['*']]


class Authorize(HTTPBearer):
    def __init__(self, scope: ODPScope):
        super().__init__()
        self.scope_id = scope.value

    async def __call__(self, request: Request) -> Authorized:
        http_auth = await super().__call__(request)
        access_token = http_auth.credentials

        hydra = AdminApi(ApiClient(Configuration(config.HYDRA.ADMIN.URL)))
        token: OAuth2TokenIntrospection = hydra.introspect_o_auth2_token(
            token=access_token,
            scope=self.scope_id,
        )
        if not token.active:
            raise HTTPException(HTTP_403_FORBIDDEN)

        # if sub == client_id it's an API call from a client,
        # using a client credentials grant
        if token.sub == token.client_id:
            client_auth = get_client_auth(token.client_id)
            try:
                return Authorized(
                    provider_ids=client_auth.scopes[self.scope_id]
                )
            except KeyError:
                raise HTTPException(HTTP_403_FORBIDDEN)

        # user-initiated API call
        user_auth = get_user_auth(token.sub, token.client_id)
        try:
            return Authorized(
                provider_ids=user_auth.scopes[self.scope_id]
            )
        except KeyError:
            raise HTTPException(HTTP_403_FORBIDDEN)
