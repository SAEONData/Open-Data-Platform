from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN

from odp import ODPScope
from odp.api2.models import CollectionModelIn, CollectionModel, CollectionSort
from odp.api2.routers import Pager, Paging, Authorize, Authorized
from odp.db import Session
from odp.db.models import Collection, Record

router = APIRouter()


@router.get(
    '/',
    response_model=List[CollectionModel],
)
async def list_collections(
        pager: Pager = Depends(Paging(CollectionSort)),
        auth: Authorized = Depends(Authorize(ODPScope.COLLECTION_READ)),
):
    stmt = (
        select(Collection, func.count(Record.id)).
        outerjoin(Record).
        group_by(Collection).
        order_by(getattr(Collection, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )
    if auth.provider_ids != '*':
        stmt = stmt.where(Collection.provider_id.in_(auth.provider_ids))

    collections = [
        CollectionModel(
            id=row.Collection.id,
            name=row.Collection.name,
            provider_id=row.Collection.provider.id,
            project_ids=[project.id for project in row.Collection.projects],
            record_count=row.count,
        )
        for row in Session.execute(stmt)
    ]

    return collections


@router.get(
    '/{collection_id}',
    response_model=CollectionModel,
)
async def get_collection(
        collection_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.COLLECTION_READ)),
):
    stmt = (
        select(Collection, func.count(Record.id)).
        outerjoin(Record).
        where(Collection.id == collection_id).
        group_by(Collection)
    )

    if not (result := Session.execute(stmt).one_or_none()):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and result.Collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return CollectionModel(
        id=result.Collection.id,
        name=result.Collection.name,
        provider_id=result.Collection.provider_id,
        project_ids=[project.id for project in result.Collection.projects],
        record_count=result.count,
    )


@router.post(
    '/',
)
async def create_collection(
        collection_in: CollectionModelIn,
        auth: Authorized = Depends(Authorize(ODPScope.COLLECTION_ADMIN)),
):
    if auth.provider_ids != '*' and collection_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.get(Collection, collection_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    collection = Collection(
        id=collection_in.id,
        name=collection_in.name,
        provider_id=collection_in.provider_id,
    )
    collection.save()


@router.put(
    '/',
)
async def update_collection(
        collection_in: CollectionModelIn,
        auth: Authorized = Depends(Authorize(ODPScope.COLLECTION_ADMIN)),
):
    if auth.provider_ids != '*' and collection_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (collection := Session.get(Collection, collection_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    collection.name = collection_in.name
    collection.provider_id = collection_in.provider_id
    collection.save()


@router.delete(
    '/{collection_id}',
)
async def delete_collection(
        collection_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.COLLECTION_ADMIN)),
):
    if not (collection := Session.get(Collection, collection_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    collection.delete()
