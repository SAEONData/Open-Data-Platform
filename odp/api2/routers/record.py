from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from jschon import URI, JSONSchema, JSON
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY

from odp import ODPScope
from odp.api2.models import RecordModel, RecordModelIn, RecordSort, RecordTagModel, RecordTagModelIn
from odp.api2.routers import Pager, Paging, Authorize, Authorized
from odp.db import Session
from odp.db.models import (
    Record,
    Collection,
    SchemaType,
    Schema,
    RecordAudit,
    AuditCommand,
    Tag,
    RecordTag,
    RecordTagAudit,
)

router = APIRouter()


async def get_metadata_schema(record_in: RecordModelIn) -> JSONSchema:
    from odp.api2 import schema_catalog
    schema = Session.get(Schema, (record_in.schema_id, SchemaType.metadata))
    return schema_catalog.get_schema(URI(schema.uri))


async def get_tag_schema(record_tag_in: RecordTagModelIn) -> JSONSchema:
    from odp.api2 import schema_catalog
    if not (tag := Session.get(Tag, record_tag_in.tag_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    schema = Session.get(Schema, (tag.schema_id, SchemaType.tag))
    return schema_catalog.get_schema(URI(schema.uri))


async def authorize_tag(record_tag_in: RecordTagModelIn, request: Request) -> Authorized:
    if not (tag := Session.get(Tag, record_tag_in.tag_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    auth = await Authorize(ODPScope(tag.scope_id))(request)
    return auth


async def authorize_untag(tag_id: str, request: Request) -> Authorized:
    if not (tag := Session.get(Tag, tag_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    auth = await Authorize(ODPScope(tag.scope_id))(request)
    return auth


@router.get(
    '/',
    response_model=List[RecordModel],
)
async def list_records(
        pager: Pager = Depends(Paging(RecordSort)),
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_READ)),
):
    stmt = (
        select(Record).
        join(Collection).
        order_by(getattr(Record, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )
    if auth.provider_ids != '*':
        stmt = stmt.where(Collection.provider_id.in_(auth.provider_ids))

    records = [
        RecordModel(
            id=row.Record.id,
            doi=row.Record.doi,
            sid=row.Record.sid,
            collection_id=row.Record.collection_id,
            schema_id=row.Record.schema_id,
            metadata=row.Record.metadata_,
            validity=row.Record.validity,
            tags=[RecordTagModel(
                tag_id=record_tag.tag_id,
                user_id=record_tag.user_id,
                user_name=record_tag.user.name,
                data=record_tag.data,
                validity=record_tag.validity,
                timestamp=record_tag.timestamp,
            ) for record_tag in row.Record.tags],
        )
        for row in Session.execute(stmt)
    ]

    return records


@router.get(
    '/{record_id}',
    response_model=RecordModel,
)
async def get_record(
        record_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_READ)),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return RecordModel(
        id=record.id,
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
        validity=record.validity,
        tags=[RecordTagModel(
            tag_id=record_tag.tag_id,
            user_id=record_tag.user_id,
            user_name=record_tag.user.name,
            data=record_tag.data,
            validity=record_tag.validity,
            timestamp=record_tag.timestamp,
        ) for record_tag in record.tags],
    )


@router.post(
    '/',
    response_model=RecordModel,
)
async def create_record(
        record_in: RecordModelIn,
        metadata_schema: JSONSchema = Depends(get_metadata_schema),
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_CREATE)),
):
    if (auth.provider_ids != '*'
            and (collection := Session.get(Collection, record_in.collection_id))
            and collection.provider_id not in auth.provider_ids):
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.execute(
        select(Record).
        where(
            ((Record.doi != None) & (Record.doi == record_in.doi)) |
            ((Record.sid != None) & (Record.sid == record_in.sid))
        )
    ).first() is not None:
        raise HTTPException(HTTP_409_CONFLICT)

    record = Record(
        doi=record_in.doi,
        sid=record_in.sid,
        collection_id=record_in.collection_id,
        schema_id=record_in.schema_id,
        schema_type=SchemaType.metadata,
        metadata_=record_in.metadata,
        validity=metadata_schema.evaluate(JSON(record_in.metadata)).output('detailed'),
    )
    record.save()

    RecordAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.insert,
        _id=record.id,
        _doi=record.doi,
        _sid=record.sid,
        _metadata=record.metadata_,
        _collection_id=record.collection_id,
        _schema_id=record.schema_id,
    ).save()

    return RecordModel(
        id=record.id,
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
        validity=record.validity,
        tags=[],
    )


@router.put(
    '/{record_id}',
    response_model=RecordModel,
)
async def update_record(
        record_id: str,
        record_in: RecordModelIn,
        metadata_schema: JSONSchema = Depends(get_metadata_schema),
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_MANAGE)),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.execute(
        select(Record).
        where(
            (Record.id != record_id) &
            (((Record.doi != None) & (Record.doi == record_in.doi)) |
             ((Record.sid != None) & (Record.sid == record_in.sid)))
        )
    ).first() is not None:
        raise HTTPException(HTTP_409_CONFLICT)

    if (
        record.doi != record_in.doi or
        record.sid != record_in.sid or
        record.collection_id != record_in.collection_id or
        record.schema_id != record_in.schema_id or
        record.metadata_ != record_in.metadata
    ):
        record.doi = record_in.doi
        record.sid = record_in.sid
        record.collection_id = record_in.collection_id
        record.schema_id = record_in.schema_id
        record.schema_type = SchemaType.metadata
        record.metadata_ = record_in.metadata
        record.validity = metadata_schema.evaluate(JSON(record_in.metadata)).output('detailed')
        record.save()

        RecordAudit(
            client_id=auth.client_id,
            user_id=auth.user_id,
            command=AuditCommand.update,
            _id=record.id,
            _doi=record.doi,
            _sid=record.sid,
            _metadata=record.metadata_,
            _collection_id=record.collection_id,
            _schema_id=record.schema_id,
        ).save()

    return RecordModel(
        id=record.id,
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
        validity=record.validity,
        tags=[RecordTagModel(
            tag_id=record_tag.tag_id,
            user_id=record_tag.user_id,
            user_name=record_tag.user.name,
            data=record_tag.data,
            validity=record_tag.validity,
            timestamp=record_tag.timestamp,
        ) for record_tag in record.tags],
    )


@router.delete(
    '/{record_id}',
)
async def delete_record(
        record_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_MANAGE)),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    record.delete()

    RecordAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.delete,
        _id=record_id,
    ).save()


@router.post(
    '/{record_id}/tag',
    response_model=RecordTagModel,
)
async def tag_record(
        record_id: str,
        record_tag_in: RecordTagModelIn,
        tag_schema: JSONSchema = Depends(get_tag_schema),
        auth: Authorized = Depends(authorize_tag),
):
    if not auth.user_id:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if record_tag := Session.get(RecordTag, (record_id, record_tag_in.tag_id, auth.user_id)):
        command = AuditCommand.update
    else:
        record_tag = RecordTag(
            record_id=record_id,
            tag_id=record_tag_in.tag_id,
            user_id=auth.user_id,
        )
        command = AuditCommand.insert
 
    if record_tag.data != record_tag_in.data:
        record_tag.data = record_tag_in.data
        record_tag.validity = tag_schema.evaluate(JSON(record_tag_in.data)).output('detailed')
        record_tag.timestamp = (timestamp := datetime.now(timezone.utc))
        record_tag.save()

        RecordTagAudit(
            client_id=auth.client_id,
            user_id=auth.user_id,
            command=command,
            timestamp=timestamp,
            _record_id=record_tag.record_id,
            _tag_id=record_tag.tag_id,
            _user_id=record_tag.user_id,
            _data=record_tag.data,
        ).save()

    return RecordTagModel(
        tag_id=record_tag.tag_id,
        user_id=record_tag.user_id,
        user_name=record_tag.user.name,
        data=record_tag.data,
        validity=record_tag.validity,
        timestamp=record_tag.timestamp,
    )


@router.delete(
    '/{record_id}/tag/{tag_id}',
)
async def untag_record(
        record_id: str,
        tag_id: str,
        auth: Authorized = Depends(authorize_untag),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (record_tag := Session.get(RecordTag, (record_id, tag_id, auth.user_id))):
        raise HTTPException(HTTP_404_NOT_FOUND)

    record_tag.delete()

    RecordTagAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.delete,
        timestamp=datetime.now(timezone.utc),
        _record_id=record_tag.record_id,
        _tag_id=record_tag.tag_id,
        _user_id=record_tag.user_id,
    ).save()
