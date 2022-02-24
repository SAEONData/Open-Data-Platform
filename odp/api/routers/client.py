from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp import ODPScope
from odp.api.lib.auth import Authorize, Authorized
# from odp.api.lib.hydra import hydra_admin_api
from odp.api.lib.paging import Page, Paginator
from odp.api.models import ClientModel, ClientModelIn
from odp.db import Session
from odp.db.models import Client, Scope

router = APIRouter()


def output_client_model(client: Client) -> ClientModel:
    # hydra_client = hydra_admin_api.get_client(client.id)
    return ClientModel(
        id=client.id,
        name=client.name,
        scope_ids=[scope.id for scope in client.scopes],
        provider_id=client.provider_id,
        # grant_types=hydra_client.grant_types,
        # response_types=hydra_client.response_types,
        # redirect_uris=hydra_client.redirect_uris,
        # post_logout_redirect_uris=hydra_client.post_logout_redirect_uris,
        # token_endpoint_auth_method=hydra_client.token_endpoint_auth_method,
        # allowed_cors_origins=hydra_client.allowed_cors_origins,
    )


@router.get(
    '/',
    response_model=Page[ClientModel],
)
async def list_clients(
        auth: Authorized = Depends(Authorize(ODPScope.CLIENT_READ)),
        paginator: Paginator = Depends(),
):
    stmt = select(Client)
    if auth.provider_ids != '*':
        stmt = stmt.where(Client.provider_id.in_(auth.provider_ids))

    return paginator.paginate(
        stmt,
        lambda row: output_client_model(row.Client),
    )


@router.get(
    '/{client_id}',
    response_model=ClientModel,
)
async def get_client(
        client_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.CLIENT_READ)),
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and client.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return output_client_model(client)


@router.post(
    '/',
)
async def create_client(
        client_in: ClientModelIn,
        auth: Authorized = Depends(Authorize(ODPScope.CLIENT_ADMIN)),
):
    if auth.provider_ids != '*' and client_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.get(Client, client_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    client = Client(
        id=client_in.id,
        name=client_in.name,
        provider_id=client_in.provider_id,
    )
    client.save()


@router.put(
    '/',
)
async def update_client(
        client_in: ClientModelIn,
        auth: Authorized = Depends(Authorize(ODPScope.CLIENT_ADMIN)),
):
    if auth.provider_ids != '*' and client_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (client := Session.get(Client, client_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    client.name = client_in.name
    client.provider_id = client_in.provider_id,
    client.save()


@router.delete(
    '/{client_id}',
)
async def delete_client(
        client_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.CLIENT_ADMIN)),
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and client.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    client.delete()


@router.put(
    '/scope/{client_id}',
)
async def set_client_scope(
        client_id: str,
        scope_ids: list[str] = Body(...),
        auth: Authorized = Depends(Authorize(ODPScope.CLIENT_ADMIN)),
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and client.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    client.scopes = [
        Session.get(Scope, scope_id)
        for scope_id in scope_ids
    ]
    client.save()
