from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN

from odp import ODPScope
from odp.api2.models import ClientModel, ClientSort
from odp.api2.routers import Pager, Paging, Authorize, Authorized
from odp.db import Session
from odp.db.models import Client, Scope

router = APIRouter()


@router.get(
    '/',
    response_model=List[ClientModel],
)
async def list_clients(
        pager: Pager = Depends(Paging(ClientSort)),
        auth: Authorized = Depends(Authorize(
            ODPScope.CLIENT_ADMIN,
            ODPScope.CLIENT_READ,
        )),
):
    stmt = (
        select(Client).
        order_by(getattr(Client, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )
    if auth.provider_ids != '*':
        stmt = stmt.where(Client.provider_id.in_(auth.provider_ids))

    clients = [
        ClientModel(
            id=row.Client.id,
            name=row.Client.name,
            scope_ids=[scope.id for scope in row.Client.scopes],
            provider_id=row.Client.provider_id,
        )
        for row in Session.execute(stmt)
    ]

    return clients


@router.get(
    '/{client_id}',
    response_model=ClientModel,
)
async def get_client(
        client_id: str,
        auth: Authorized = Depends(Authorize(
            ODPScope.CLIENT_ADMIN,
            ODPScope.CLIENT_READ,
        )),
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and client.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return ClientModel(
        id=client.id,
        name=client.name,
        scope_ids=[scope.id for scope in client.scopes],
        provider_id=client.provider_id,
    )


@router.post(
    '/',
)
async def create_client(
        client_in: ClientModel,
        auth: Authorized = Depends(Authorize(
            ODPScope.CLIENT_ADMIN,
        )),
):
    if auth.provider_ids != '*' and client_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.get(Client, client_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    client = Client(
        id=client_in.id,
        name=client_in.name,
        scopes=[
            Session.get(Scope, scope_id)
            for scope_id in client_in.scope_ids
        ],
        provider_id=client_in.provider_id,
    )
    client.save()


@router.put(
    '/',
)
async def update_client(
        client_in: ClientModel,
        auth: Authorized = Depends(Authorize(
            ODPScope.CLIENT_ADMIN,
        )),
):
    if auth.provider_ids != '*' and client_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (client := Session.get(Client, client_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    client.name = client_in.name
    client.scopes = [
        Session.get(Scope, scope_id)
        for scope_id in client_in.scope_ids
    ]
    client.provider_id = client_in.provider_id,
    client.save()


@router.delete(
    '/{client_id}',
)
async def delete_client(
        client_id: str,
        auth: Authorized = Depends(Authorize(
            ODPScope.CLIENT_ADMIN,
        )),
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and client.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    client.delete()
