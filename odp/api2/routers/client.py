from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from odp.api2.models import ClientIn, ClientOut, ClientSort
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import Client

router = APIRouter()


@router.get('/', response_model=List[ClientOut])
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
        ClientOut(
            id=row.Client.id,
            name=row.Client.name,
        )
        for row in Session.execute(stmt)
    ]

    return clients


@router.get('/{client_id}', response_model=ClientOut)
async def get_client(
        client_id: str,
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return ClientOut(
        id=client.id,
        name=client.name,
    )


@router.post('/')
async def create_client(
        client_in: ClientIn,
):
    if Session.get(Client, client_in.id):
        raise HTTPException(status.HTTP_409_CONFLICT)

    client = Client(
        id=client_in.id,
        name=client_in.name,
    )
    client.save()


@router.put('/')
async def update_client(
        client_in: ClientIn,
):
    if not (client := Session.get(Client, client_in.id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    client.name = client_in.name
    client.save()


@router.delete('/{client_id}')
async def delete_client(
        client_id: str,
):
    if not (client := Session.get(Client, client_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    client.delete()
