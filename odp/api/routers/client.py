from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp import ODPScope
from odp.api.lib.auth import Authorize, Authorized
from odp.api.lib.paging import Page, Paginator
from odp.api.models import ClientModel
from odp.db import Session
from odp.db.models import Client, Scope

router = APIRouter()


def select_scopes(client_in: ClientModel) -> list[Scope]:
    # silently ignore unknown scope ids
    return Session.execute(
        select(Scope).
        where(Scope.id.in_(client_in.scope_ids))
    ).scalars().all()


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
        lambda row: ClientModel(
            id=row.Client.id,
            name='',
            scope_ids=[scope.id for scope in row.Client.scopes],
            provider_id=row.Client.provider_id,
        )
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

    return ClientModel(
        id=client.id,
        name='',
        scope_ids=[scope.id for scope in client.scopes],
        provider_id=client.provider_id,
    )


@router.post(
    '/',
)
async def create_client(
        client_in: ClientModel,
        auth: Authorized = Depends(Authorize(ODPScope.CLIENT_ADMIN)),
):
    if auth.provider_ids != '*' and client_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.get(Client, client_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    client = Client(
        id=client_in.id,
        scopes=select_scopes(client_in),
        provider_id=client_in.provider_id,
    )
    client.save()


@router.put(
    '/',
)
async def update_client(
        client_in: ClientModel,
        auth: Authorized = Depends(Authorize(ODPScope.CLIENT_ADMIN)),
):
    if auth.provider_ids != '*' and client_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (client := Session.get(Client, client_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    client.scopes = select_scopes(client_in)
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
