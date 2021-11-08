from typing import List

from fastapi import APIRouter, Depends, HTTPException
from jschon import URI, JSONSchema, JSON
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN

from odp import ODPScope
from odp.api2.models import RecordModel, RecordModelIn, RecordSort
from odp.api2.routers import Pager, Paging, Authorize, Authorized
from odp.db import Session
from odp.db.models import Record, Collection, SchemaType, Schema

router = APIRouter()


async def get_jsonschema(record_in: RecordModelIn) -> JSONSchema:
    from odp.api2 import catalog
    schema = Session.get(Schema, (record_in.schema_id, SchemaType.metadata))
    return catalog.get_schema(URI(schema.uri))


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
        order_by(getattr(Record, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )
    if auth.provider_ids != '*':
        stmt = stmt.where(Record.collection.provider_id.in_(auth.provider_ids))

    records = [
        RecordModel(
            id=row.Record.id,
            doi=row.Record.doi,
            sid=row.Record.sid,
            collection_id=row.Record.collection_id,
            schema_id=row.Record.schema_id,
            metadata=row.Record.metadata_,
            validity=row.Record.validity,
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
    )


@router.post(
    '/',
)
async def create_record(
        record_in: RecordModelIn,
        jsonschema: JSONSchema = Depends(get_jsonschema),
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_CREATE)),
):
    if (auth.provider_ids != '*'
            and (collection := Session.get(Collection, record_in.collection_id))
            and collection.provider_id not in auth.provider_ids):
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.execute(
        select(Record).
        where((Record.doi == record_in.doi) | (Record.sid == record_in.sid))
    ).first() is not None:
        raise HTTPException(HTTP_409_CONFLICT)

    record = Record(
        doi=record_in.doi,
        sid=record_in.sid,
        collection_id=record_in.collection_id,
        schema_id=record_in.schema_id,
        schema_type=SchemaType.metadata,
        metadata_=record_in.metadata,
        validity=jsonschema.evaluate(JSON(record_in.metadata)).output('detailed'),
    )
    record.save()


@router.put(
    '/',
)
async def update_record(
        record_in: RecordModelIn,
        jsonschema: JSONSchema = Depends(get_jsonschema),
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_MANAGE)),
):
    if (auth.provider_ids != '*'
            and (collection := Session.get(Collection, record_in.collection_id))
            and collection.provider_id not in auth.provider_ids):
        raise HTTPException(HTTP_403_FORBIDDEN)

    if (record := Session.execute(
            select(Record).
            where((Record.doi == record_in.doi) | (Record.sid == record_in.sid))
    ).scalar_one_or_none()) is None:
        raise HTTPException(HTTP_404_NOT_FOUND)

    record.doi = record_in.doi
    record.sid = record_in.sid
    record.collection_id = record_in.collection_id
    record.schema_id = record_in.schema_id
    record.schema_type = SchemaType.metadata
    record.metadata_ = record_in.metadata
    record.validity = jsonschema.evaluate(JSON(record_in.metadata)).output('detailed')
    record.save()


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
