from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp import ODPScope
from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.models import ProviderModel, ProviderModelIn
from odp.db import Session
from odp.db.models import Provider

router = APIRouter()


@router.get(
    '/',
    response_model=Page[ProviderModel],
    dependencies=[Depends(Authorize(ODPScope.PROVIDER_READ))],
)
async def list_providers(
        paginator: Paginator = Depends(),
):
    return paginator.paginate(
        select(Provider),
        lambda row: ProviderModel(
            id=row.Provider.id,
            name=row.Provider.name,
            collection_ids=[collection.id for collection in row.Provider.collections],
        )
    )


@router.get(
    '/{provider_id}',
    response_model=ProviderModel,
    dependencies=[Depends(Authorize(ODPScope.PROVIDER_READ))],
)
async def get_provider(
        provider_id: str,
):
    if not (provider := Session.get(Provider, provider_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return ProviderModel(
        id=provider.id,
        name=provider.name,
        collection_ids=[collection.id for collection in provider.collections],
    )


@router.post(
    '/',
    dependencies=[Depends(Authorize(ODPScope.PROVIDER_ADMIN))],
)
async def create_provider(
        provider_in: ProviderModelIn,
):
    if Session.get(Provider, provider_in.id):
        raise HTTPException(HTTP_409_CONFLICT, 'Provider id is already in use')

    provider = Provider(
        id=provider_in.id,
        name=provider_in.name,
    )
    provider.save()


@router.put(
    '/',
    dependencies=[Depends(Authorize(ODPScope.PROVIDER_ADMIN))],
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
    dependencies=[Depends(Authorize(ODPScope.PROVIDER_ADMIN))],
)
async def delete_provider(
        provider_id: str,
):
    if not (provider := Session.get(Provider, provider_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    provider.delete()
