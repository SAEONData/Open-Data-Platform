from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp.api2.models import ProviderModelIn, ProviderModel, ProviderSort
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import Provider

router = APIRouter()


@router.get(
    '/',
    response_model=List[ProviderModel],
)
async def list_providers(
        pager: Pager = Depends(Paging(ProviderSort)),
):
    stmt = (
        select(Provider).
        order_by(getattr(Provider, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    providers = [
        ProviderModel(
            id=row.Provider.id,
            name=row.Provider.name,
            role_ids=[role.id for role in row.Provider.roles],
            collection_ids=[collection.id for collection in row.Provider.collections],
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
):
    if not (provider := Session.get(Provider, provider_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return ProviderModel(
        id=provider.id,
        name=provider.name,
        role_ids=[role.id for role in provider.roles],
        collection_ids=[collection.id for collection in provider.collections],
    )


@router.post(
    '/',
)
async def create_provider(
        provider_in: ProviderModelIn,
):
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
):
    if not (provider := Session.get(Provider, provider_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    provider.name = provider_in.name
    provider.save()


@router.delete(
    '/{provider_id}',
)
async def delete_provider(
        provider_id: str,
):
    if not (provider := Session.get(Provider, provider_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    provider.delete()
