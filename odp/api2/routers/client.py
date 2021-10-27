from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp import ODPScope
from odp.api2.models import ClientModel, ClientSort
from odp.api2.routers import Pager, Paging, Authorize
from odp.db import Session
from odp.db.models import Client, Scope

router = APIRouter()


@router.get(
    '/',
    response_model=List[ClientModel],
    dependencies=[Depends(Authorize(ODPScope.CLIENT_READ))],
)
async def list_clients(
        pager: Pager = Depends(Paging(ClientSort)),
):
    stmt = (
        select(Client).
        order_by(getattr(Client, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    clients = [
        ClientModel(
            id=row.Client.id,
            name=row.Client.name,
            scope_ids=[scope.id for scope in row.Client.scopes],
        )
        for row in Session.execute(stmt)
    ]

    return clients


@router.get(
    '/{client_id}',
    response_model=ClientModel,
    dependencies=[Depends(Authorize(ODPScope.CLIENT_READ))],
)
async def get_client(
        client_id: str,
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return ClientModel(
        id=client.id,
        name=client.name,
        scope_ids=[scope.id for scope in client.scopes],
    )


@router.post(
    '/',
    dependencies=[Depends(Authorize(ODPScope.CLIENT_ADMIN))],
)
async def create_client(
        client_in: ClientModel,
):
    if Session.get(Client, client_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    client = Client(
        id=client_in.id,
        name=client_in.name,
        scopes=[
            Session.get(Scope, scope_id)
            for scope_id in client_in.scope_ids
        ],
    )
    client.save()


@router.put(
    '/',
    dependencies=[Depends(Authorize(ODPScope.CLIENT_ADMIN))],
)
async def update_client(
        client_in: ClientModel,
):
    if not (client := Session.get(Client, client_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    client.name = client_in.name
    client.scopes = [
        Session.get(Scope, scope_id)
        for scope_id in client_in.scope_ids
    ]
    client.save()


@router.delete(
    '/{client_id}',
    dependencies=[Depends(Authorize(ODPScope.CLIENT_ADMIN))],
)
async def delete_client(
        client_id: str,
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    client.delete()
