from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN

from odp import ODPScope
from odp.api2.models import ProviderModelIn, ProviderModel, ProviderSort
from odp.api2.routers import Pager, Paging, Authorize, Authorized
from odp.db import Session
from odp.db.models import Provider

router = APIRouter()


@router.get(
    '/',
    response_model=List[ProviderModel],
)
async def list_providers(
        pager: Pager = Depends(Paging(ProviderSort)),
        auth: Authorized = Depends(Authorize(
            ODPScope.PROVIDER_ADMIN,
            ODPScope.PROVIDER_READ,
        )),
):
    stmt = (
        select(Provider).
        order_by(getattr(Provider, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )
    if auth.provider_ids != '*':
        stmt = stmt.where(Provider.id.in_(auth.provider_ids))

    providers = [
        ProviderModel(
            id=row.Provider.id,
            name=row.Provider.name,
            collection_ids=[collection.id for collection in row.Provider.collections],
            client_ids=[client.id for client in row.Provider.clients],
            role_ids=[role.id for role in row.Provider.roles],
        )
        for row in Session.execute(stmt)
    ]

    return providers


@router.get(
    '/{provider_id}',
    response_model=ProviderModel,
)
async def get_provider(
        provider_id: str,
        auth: Authorized = Depends(Authorize(
            ODPScope.PROVIDER_ADMIN,
            ODPScope.PROVIDER_READ,
        )),
):
    if auth.provider_ids != '*' and provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (provider := Session.get(Provider, provider_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return ProviderModel(
        id=provider.id,
        name=provider.name,
        collection_ids=[collection.id for collection in provider.collections],
        client_ids=[client.id for client in provider.clients],
        role_ids=[role.id for role in provider.roles],
    )


@router.post(
    '/',
)
async def create_provider(
        provider_in: ProviderModelIn,
        auth: Authorized = Depends(Authorize(
            ODPScope.PROVIDER_ADMIN,
        )),
):
    if auth.provider_ids != '*':
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.get(Provider, provider_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    provider = Provider(
        id=provider_in.id,
        name=provider_in.name,
    )
    provider.save()


@router.put(
    '/',
)
async def update_provider(
        provider_in: ProviderModelIn,
        auth: Authorized = Depends(Authorize(
            ODPScope.PROVIDER_ADMIN,
        )),
):
    if auth.provider_ids != '*' and provider_in.id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (provider := Session.get(Provider, provider_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    provider.name = provider_in.name
    provider.save()


@router.delete(
    '/{provider_id}',
)
async def delete_provider(
        provider_id: str,
        auth: Authorized = Depends(Authorize(
            ODPScope.PROVIDER_ADMIN,
        )),
):
    if auth.provider_ids != '*' and provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (provider := Session.get(Provider, provider_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    provider.delete()
