from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from jschon import JSONSchema, JSON
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY

from odp import ODPScope
from odp.api.lib.auth import Authorize, Authorized, FlagAuthorize, UnflagAuthorize, TagAuthorize, UntagAuthorize
from odp.api.lib.paging import Pager, Paging
from odp.api.lib.schema import get_metadata_schema, get_flag_schema, get_tag_schema
from odp.api.models import RecordModel, RecordModelIn, RecordSort, TagInstanceModel, TagInstanceModelIn, FlagInstanceModel, FlagInstanceModelIn
from odp.db import Session
from odp.db.models import Record, Collection, SchemaType, RecordAudit, AuditCommand, RecordTag, RecordTagAudit, RecordFlag, RecordFlagAudit

router = APIRouter()


def output_record_model(record: Record) -> RecordModel:
    return RecordModel(
        id=record.id,
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
        validity=record.validity,
        timestamp=record.timestamp,
        flags=[
            output_record_flag_model(record_flag)
            for record_flag in record.flags
        ],
        tags=[
            output_record_tag_model(record_tag)
            for record_tag in record.tags
        ],
    )


def output_record_flag_model(record_flag: RecordFlag) -> FlagInstanceModel:
    return FlagInstanceModel(
        flag_id=record_flag.flag_id,
        user_id=record_flag.user_id,
        user_name=record_flag.user.name if record_flag.user_id else None,
        data=record_flag.data,
        timestamp=record_flag.timestamp,
    )


def output_record_tag_model(record_tag: RecordTag) -> TagInstanceModel:
    return TagInstanceModel(
        tag_id=record_tag.tag_id,
        user_id=record_tag.user_id,
        user_name=record_tag.user.name if record_tag.user_id else None,
        data=record_tag.data,
        timestamp=record_tag.timestamp,
    )


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
        output_record_model(row.Record)
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

    return output_record_model(record)


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
        timestamp=(timestamp := datetime.now(timezone.utc)),
    )
    record.save()

    RecordAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.insert,
        timestamp=timestamp,
        _id=record.id,
        _doi=record.doi,
        _sid=record.sid,
        _metadata=record.metadata_,
        _collection_id=record.collection_id,
        _schema_id=record.schema_id,
    ).save()

    return output_record_model(record)


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

    if record.doi is not None and record.doi != record_in.doi:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'The DOI cannot be changed or removed')

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
        record.timestamp = (timestamp := datetime.now(timezone.utc))
        record.save()

        RecordAudit(
            client_id=auth.client_id,
            user_id=auth.user_id,
            command=AuditCommand.update,
            timestamp=timestamp,
            _id=record.id,
            _doi=record.doi,
            _sid=record.sid,
            _metadata=record.metadata_,
            _collection_id=record.collection_id,
            _schema_id=record.schema_id,
        ).save()

    return output_record_model(record)


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
        timestamp=datetime.now(timezone.utc),
        _id=record_id,
    ).save()


@router.post(
    '/{record_id}/tag',
    response_model=TagInstanceModel,
)
async def tag_record(
        record_id: str,
        tag_instance_in: TagInstanceModelIn,
        tag_schema: JSONSchema = Depends(get_tag_schema),
        auth: Authorized = Depends(TagAuthorize()),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if record_tag := Session.execute(
        select(RecordTag).
        where(RecordTag.record_id == record_id).
        where(RecordTag.tag_id == tag_instance_in.tag_id).
        where(RecordTag.user_id == auth.user_id)
    ).scalar_one_or_none():
        command = AuditCommand.update
    else:
        record_tag = RecordTag(
            record_id=record_id,
            tag_id=tag_instance_in.tag_id,
            user_id=auth.user_id,
        )
        command = AuditCommand.insert

    if record_tag.data != tag_instance_in.data:
        validity = tag_schema.evaluate(JSON(tag_instance_in.data)).output('detailed')
        if not validity['valid']:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, validity)

        record_tag.data = tag_instance_in.data
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

    return output_record_tag_model(record_tag)


@router.delete(
    '/{record_id}/tag/{tag_id}',
)
async def untag_record(
        record_id: str,
        tag_id: str,
        auth: Authorized = Depends(UntagAuthorize()),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (record_tag := Session.execute(
        select(RecordTag).
        where(RecordTag.record_id == record_id).
        where(RecordTag.tag_id == tag_id).
        where(RecordTag.user_id == auth.user_id)
    ).scalar_one_or_none()):
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


@router.post(
    '/{record_id}/flag',
    response_model=FlagInstanceModel,
)
async def flag_record(
        record_id: str,
        flag_instance_in: FlagInstanceModelIn,
        flag_schema: JSONSchema = Depends(get_flag_schema),
        auth: Authorized = Depends(FlagAuthorize()),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if record_flag := Session.get(RecordFlag, (record_id, flag_instance_in.flag_id)):
        command = AuditCommand.update
    else:
        record_flag = RecordFlag(
            record_id=record_id,
            flag_id=flag_instance_in.flag_id,
        )
        command = AuditCommand.insert

    if record_flag.data != flag_instance_in.data:
        validity = flag_schema.evaluate(JSON(flag_instance_in.data)).output('detailed')
        if not validity['valid']:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, validity)

        record_flag.user_id = auth.user_id
        record_flag.data = flag_instance_in.data
        record_flag.timestamp = (timestamp := datetime.now(timezone.utc))
        record_flag.save()

        RecordFlagAudit(
            client_id=auth.client_id,
            user_id=auth.user_id,
            command=command,
            timestamp=timestamp,
            _record_id=record_flag.record_id,
            _flag_id=record_flag.flag_id,
            _user_id=record_flag.user_id,
            _data=record_flag.data,
        ).save()

    return output_record_flag_model(record_flag)


@router.delete(
    '/{record_id}/flag/{flag_id}',
)
async def unflag_record(
        record_id: str,
        flag_id: str,
        auth: Authorized = Depends(UnflagAuthorize()),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and record.collection.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (record_flag := Session.get(RecordFlag, (record_id, flag_id))):
        raise HTTPException(HTTP_404_NOT_FOUND)

    record_flag.delete()

    RecordFlagAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.delete,
        timestamp=datetime.now(timezone.utc),
        _record_id=record_flag.record_id,
        _flag_id=record_flag.flag_id,
    ).save()
