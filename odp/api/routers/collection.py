from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from jschon import URI, JSONSchema, JSON
from sqlalchemy import select, func
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY

from odp import ODPScope
from odp.api.models import CollectionModelIn, CollectionModel, CollectionSort, CollectionTagModel, CollectionTagModelIn
from odp.api.routers import Pager, Paging, Authorize, Authorized
from odp.db import Session
from odp.db.models import Collection, Record, Tag, CollectionTag, CollectionTagAudit, AuditCommand, Schema, SchemaType

router = APIRouter()


async def get_tag_schema(collection_tag_in: CollectionTagModelIn) -> JSONSchema:
    from odp.api import schema_catalog
    if not (tag := Session.get(Tag, collection_tag_in.tag_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    schema = Session.get(Schema, (tag.schema_id, SchemaType.tag))
    return schema_catalog.get_schema(URI(schema.uri))


async def authorize_tag(collection_tag_in: CollectionTagModelIn, request: Request) -> Authorized:
    if not (tag := Session.get(Tag, collection_tag_in.tag_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    authorizer = Authorize(ODPScope(tag.scope_id))
    return await authorizer(request)


async def authorize_untag(tag_id: str, request: Request) -> Authorized:
    if not (tag := Session.get(Tag, tag_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    authorizer = Authorize(ODPScope(tag.scope_id))
    return await authorizer(request)


def output_collection_model(result) -> CollectionModel:
    return CollectionModel(
        id=result.Collection.id,
        name=result.Collection.name,
        provider_id=result.Collection.provider_id,
        project_ids=[project.id for project in result.Collection.projects],
        record_count=result.count,
        tags=[
            output_collection_tag_model(collection_tag)
            for collection_tag in result.Collection.tags
        ],
    )


def output_collection_tag_model(collection_tag: CollectionTag) -> CollectionTagModel:
    return CollectionTagModel(
        tag_id=collection_tag.tag_id,
        user_id=collection_tag.user_id,
        user_name=collection_tag.user.name if collection_tag.user_id else None,
        data=collection_tag.data,
        timestamp=collection_tag.timestamp,
    )


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
        output_collection_model(row)
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

    return output_collection_model(result)


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


@router.post(
    '/{collection_id}/tag',
    response_model=CollectionTagModel,
)
async def tag_collection(
        collection_id: str,
        collection_tag_in: CollectionTagModelIn,
        tag_schema: JSONSchema = Depends(get_tag_schema),
        auth: Authorized = Depends(authorize_tag),
):
    if not (collection := Session.get(Collection, collection_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if collection_tag := Session.execute(
        select(CollectionTag).
        where(CollectionTag.collection_id == collection_id).
        where(CollectionTag.tag_id == collection_tag_in.tag_id).
        where(CollectionTag.user_id == auth.user_id)
    ).scalar_one_or_none():
        command = AuditCommand.update
    else:
        collection_tag = CollectionTag(
            collection_id=collection_id,
            tag_id=collection_tag_in.tag_id,
            user_id=auth.user_id,
        )
        command = AuditCommand.insert

    if collection_tag.data != collection_tag_in.data:
        validity = tag_schema.evaluate(JSON(collection_tag_in.data)).output('detailed')
        if not validity['valid']:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, validity)

        collection_tag.data = collection_tag_in.data
        collection_tag.timestamp = (timestamp := datetime.now(timezone.utc))
        collection_tag.save()

        CollectionTagAudit(
            client_id=auth.client_id,
            user_id=auth.user_id,
            command=command,
            timestamp=timestamp,
            _collection_id=collection_tag.collection_id,
            _tag_id=collection_tag.tag_id,
            _user_id=collection_tag.user_id,
            _data=collection_tag.data,
        ).save()

    return output_collection_tag_model(collection_tag)


@router.delete(
    '/{collection_id}/tag/{tag_id}',
)
async def untag_collection(
        collection_id: str,
        tag_id: str,
        auth: Authorized = Depends(authorize_untag),
):
    if not (collection := Session.get(Collection, collection_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (collection_tag := Session.execute(
        select(CollectionTag).
        where(CollectionTag.collection_id == collection_id).
        where(CollectionTag.tag_id == tag_id).
        where(CollectionTag.user_id == auth.user_id)
    ).scalar_one_or_none()):
        raise HTTPException(HTTP_404_NOT_FOUND)

    collection_tag.delete()

    CollectionTagAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.delete,
        timestamp=datetime.now(timezone.utc),
        _collection_id=collection_tag.collection_id,
        _tag_id=collection_tag.tag_id,
        _user_id=collection_tag.user_id,
    ).save()
