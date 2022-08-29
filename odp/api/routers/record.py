from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from jschon import JSON, JSONSchema
from sqlalchemy import literal_column, null, select, union_all
from sqlalchemy.orm import aliased
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from odp import ODPCollectionTag, ODPScope
from odp.api.lib.auth import Authorize, Authorized, TagAuthorize, UntagAuthorize
from odp.api.lib.paging import Page, Paginator
from odp.api.lib.schema import get_metadata_schema, get_tag_schema
from odp.api.lib.utils import output_published_record_model, output_tag_instance_model
from odp.api.models import (AuditModel, CatalogRecordModel, RecordAuditModel, RecordModel, RecordModelIn, RecordTagAuditModel, TagInstanceModel,
                            TagInstanceModelIn)
from odp.db import Session
from odp.db.models import (AuditCommand, CatalogRecord, Collection, CollectionTag, PublishedDOI, Record, RecordAudit, RecordTag, RecordTagAudit,
                           SchemaType, Tag, TagCardinality, TagType, User)

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
        timestamp=record.timestamp.isoformat(),
        tags=[
                 output_tag_instance_model(collection_tag)
                 for collection_tag in record.collection.tags
             ] + [
                 output_tag_instance_model(record_tag)
                 for record_tag in record.tags
             ],
        published_catalog_ids=[
            catalog_record.catalog_id
            for catalog_record in record.catalog_records
            if catalog_record.published
        ]
    )


def output_catalog_record_model(catalog_record: CatalogRecord) -> CatalogRecordModel:
    return CatalogRecordModel(
        catalog_id=catalog_record.catalog_id,
        record_id=catalog_record.record_id,
        timestamp=catalog_record.timestamp.isoformat(),
        published=catalog_record.published,
        published_record=output_published_record_model(catalog_record),
    )


def get_validity(metadata: dict[str, Any], schema: JSONSchema) -> Any:
    if (result := schema.evaluate(JSON(metadata))).valid:
        return result.output('flag')

    return result.output('detailed')


@router.get(
    '/',
    response_model=Page[RecordModel],
)
async def list_records(
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_READ)),
        paginator: Paginator = Depends(),
        collection_id: list[str] = Query(None),
):
    stmt = (
        select(Record).
        join(Collection)
    )
    if auth.collection_ids != '*':
        stmt = stmt.where(Collection.id.in_(auth.collection_ids))
    if collection_id:
        stmt = stmt.where(Collection.id.in_(collection_id))

    return paginator.paginate(
        stmt,
        lambda row: output_record_model(row.Record),
        custom_sort='collection.id, record.doi, record.sid',
    )


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

    if auth.collection_ids != '*' and record.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return output_record_model(record)


@router.post(
    '/',
    response_model=RecordModel,
)
async def create_record(
        record_in: RecordModelIn,
        metadata_schema: JSONSchema = Depends(get_metadata_schema),
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_WRITE)),
):
    return _create_record(record_in, metadata_schema, auth)


@router.post(
    '/admin/',
    response_model=RecordModel,
)
async def admin_create_record(
        record_in: RecordModelIn,
        metadata_schema: JSONSchema = Depends(get_metadata_schema),
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_ADMIN)),
):
    return _create_record(record_in, metadata_schema, auth, True)


def _create_record(
        record_in: RecordModelIn,
        metadata_schema: JSONSchema,
        auth: Authorized,
        ignore_collection_tags: bool = False,
) -> RecordModel:
    if auth.collection_ids != '*' and record_in.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not ignore_collection_tags and Session.execute(
        select(CollectionTag).
        where(CollectionTag.collection_id == record_in.collection_id).
        where(CollectionTag.tag_id == ODPCollectionTag.FROZEN)
    ).first() is not None:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'A record cannot be added to a frozen collection')

    if record_in.doi and Session.execute(
        select(Record).
        where(Record.doi == record_in.doi)
    ).first() is not None:
        raise HTTPException(HTTP_409_CONFLICT, 'DOI is already in use')

    if record_in.sid and Session.execute(
        select(Record).
        where(Record.sid == record_in.sid)
    ).first() is not None:
        raise HTTPException(HTTP_409_CONFLICT, 'SID is already in use')

    record = Record(
        doi=record_in.doi,
        sid=record_in.sid,
        collection_id=record_in.collection_id,
        schema_id=record_in.schema_id,
        schema_type=SchemaType.metadata,
        metadata_=record_in.metadata,
        validity=get_validity(record_in.metadata, metadata_schema),
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
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_WRITE)),
):
    if auth.collection_ids != '*' and record_in.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return _set_record(False, record, record_in, metadata_schema, auth)


@router.put(
    '/admin/{record_id}',
    response_model=RecordModel,
)
async def admin_set_record(
        # this route allows a record to be created with an externally
        # generated id, so we must validate that it is a uuid
        record_id: UUID,
        record_in: RecordModelIn,
        metadata_schema: JSONSchema = Depends(get_metadata_schema),
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_ADMIN)),
):
    if auth.collection_ids != '*' and record_in.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    create = False
    record = Session.get(Record, str(record_id))
    if not record:
        create = True
        record = Record(id=str(record_id))

    return _set_record(create, record, record_in, metadata_schema, auth, True)


def _set_record(
        create: bool,
        record: Record,
        record_in: RecordModelIn,
        metadata_schema: JSONSchema,
        auth: Authorized,
        ignore_collection_tags: bool = False,
) -> RecordModel:
    if not create and auth.collection_ids != '*' and record.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not ignore_collection_tags and Session.execute(
        select(CollectionTag).
        where(CollectionTag.collection_id == record_in.collection_id).
        where(CollectionTag.tag_id.in_((ODPCollectionTag.FROZEN, ODPCollectionTag.READY)))
    ).first() is not None:
        raise HTTPException(
            HTTP_422_UNPROCESSABLE_ENTITY,
            'Cannot update a record belonging to a ready or frozen collection',
        )

    if record_in.doi and Session.execute(
        select(Record).
        where(Record.id != record.id).
        where(Record.doi == record_in.doi)
    ).first() is not None:
        raise HTTPException(HTTP_409_CONFLICT, 'DOI is already in use')

    if record_in.sid and Session.execute(
        select(Record).
        where(Record.id != record.id).
        where(Record.sid == record_in.sid)
    ).first() is not None:
        raise HTTPException(HTTP_409_CONFLICT, 'SID is already in use')

    if (record.doi is not None and record.doi != record_in.doi and
            Session.get(PublishedDOI, record.doi)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'The DOI has been published and cannot be modified.')

    if (
        create or
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
        record.validity = get_validity(record_in.metadata, metadata_schema)
        record.timestamp = (timestamp := datetime.now(timezone.utc))
        record.save()

        RecordAudit(
            client_id=auth.client_id,
            user_id=auth.user_id,
            command=AuditCommand.insert if create else AuditCommand.update,
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
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_WRITE)),
):
    _delete_record(record_id, auth)


@router.delete(
    '/admin/{record_id}',
)
async def admin_delete_record(
        record_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_ADMIN)),
):
    _delete_record(record_id, auth, True)


def _delete_record(
        record_id: str,
        auth: Authorized,
        ignore_collection_tags: bool = False,
) -> None:
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.collection_ids != '*' and record.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not ignore_collection_tags and Session.execute(
        select(CollectionTag).
        where(CollectionTag.collection_id == record.collection_id).
        where(CollectionTag.tag_id.in_((ODPCollectionTag.FROZEN, ODPCollectionTag.READY)))
    ).first() is not None:
        raise HTTPException(
            HTTP_422_UNPROCESSABLE_ENTITY,
            'Cannot delete a record belonging to a ready or frozen collection',
        )

    if record.doi is not None and Session.get(PublishedDOI, record.doi):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'The DOI has been published and cannot be deleted.')

    RecordAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.delete,
        timestamp=datetime.now(timezone.utc),
        _id=record.id,
    ).save()

    record.delete()


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

    if auth.collection_ids != '*' and record.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (tag := Session.get(Tag, (tag_instance_in.tag_id, TagType.record))):
        raise HTTPException(HTTP_404_NOT_FOUND)

    # only one tag instance per record is allowed
    # update allowed only by the user who did the insert
    if tag.cardinality == TagCardinality.one:
        if record_tag := Session.execute(
                select(RecordTag).
                where(RecordTag.record_id == record_id).
                where(RecordTag.tag_id == tag_instance_in.tag_id)
        ).scalar_one_or_none():
            if record_tag.user_id != auth.user_id:
                raise HTTPException(HTTP_409_CONFLICT, 'Cannot update a tag set by another user')
            command = AuditCommand.update
        else:
            command = AuditCommand.insert

    # one tag instance per user per record is allowed
    # update a user's existing tag instance if found
    elif tag.cardinality == TagCardinality.user:
        if record_tag := Session.execute(
                select(RecordTag).
                where(RecordTag.record_id == record_id).
                where(RecordTag.tag_id == tag_instance_in.tag_id).
                where(RecordTag.user_id == auth.user_id)
        ).scalar_one_or_none():
            command = AuditCommand.update
        else:
            command = AuditCommand.insert

    # multiple tag instances are allowed per user per record
    # can only insert/delete
    elif tag.cardinality == TagCardinality.multi:
        command = AuditCommand.insert

    else:
        assert False

    if command == AuditCommand.insert:
        record_tag = RecordTag(
            record_id=record_id,
            tag_id=tag_instance_in.tag_id,
            tag_type=TagType.record,
            user_id=auth.user_id,
        )

    if record_tag.data != tag_instance_in.data:
        validity = tag_schema.evaluate(JSON(tag_instance_in.data)).output('detailed')
        if not validity['valid']:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, validity)

        record_tag.data = tag_instance_in.data
        record_tag.timestamp = (timestamp := datetime.now(timezone.utc))
        record_tag.save()

        record.timestamp = timestamp
        record.save()

        RecordTagAudit(
            client_id=auth.client_id,
            user_id=auth.user_id,
            command=command,
            timestamp=timestamp,
            _id=record_tag.id,
            _record_id=record_tag.record_id,
            _tag_id=record_tag.tag_id,
            _user_id=record_tag.user_id,
            _data=record_tag.data,
        ).save()

    return output_tag_instance_model(record_tag)


@router.delete(
    '/{record_id}/tag/{tag_instance_id}',
)
async def untag_record(
        record_id: str,
        tag_instance_id: str,
        auth: Authorized = Depends(UntagAuthorize(TagType.record)),
):
    _untag_record(record_id, tag_instance_id, auth)


@router.delete(
    '/admin/{record_id}/tag/{tag_instance_id}',
)
async def admin_untag_record(
        record_id: str,
        tag_instance_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_ADMIN)),
):
    _untag_record(record_id, tag_instance_id, auth, True)


def _untag_record(
        record_id: str,
        tag_instance_id: str,
        auth: Authorized,
        ignore_user_id: bool = False,
) -> None:
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.collection_ids != '*' and record.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (record_tag := Session.execute(
        select(RecordTag).
        where(RecordTag.id == tag_instance_id).
        where(RecordTag.record_id == record_id)
    ).scalar_one_or_none()):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if not ignore_user_id and record_tag.user_id != auth.user_id:
        raise HTTPException(HTTP_403_FORBIDDEN)

    record_tag.delete()

    record.timestamp = (timestamp := datetime.now(timezone.utc))
    record.save()

    RecordTagAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.delete,
        timestamp=timestamp,
        _id=record_tag.id,
        _record_id=record_tag.record_id,
        _tag_id=record_tag.tag_id,
        _user_id=record_tag.user_id,
    ).save()


@router.get(
    '/{record_id}/catalog',
    response_model=Page[CatalogRecordModel],
)
async def list_catalog_records(
        record_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_READ)),
        paginator: Paginator = Depends(),
):
    if not (record := Session.get(Record, record_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.collection_ids != '*' and record.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    stmt = (
        select(CatalogRecord).
        where(CatalogRecord.record_id == record_id)
    )
    paginator.sort = 'catalog_id'

    return paginator.paginate(
        stmt,
        lambda row: output_catalog_record_model(row.CatalogRecord),
    )


@router.get(
    '/{record_id}/catalog/{catalog_id}',
    response_model=CatalogRecordModel,
)
async def get_catalog_record(
        record_id: str,
        catalog_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_READ)),
):
    if not (catalog_record := Session.get(CatalogRecord, (catalog_id, record_id))):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.collection_ids != '*' and catalog_record.record.collection_id not in auth.collection_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return output_catalog_record_model(catalog_record)


@router.get(
    '/{record_id}/audit',
    response_model=Page[AuditModel],
)
async def get_record_audit_log(
        record_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_READ)),
        paginator: Paginator = Depends(),
):
    # allow retrieving the audit log for a deleted record,
    # except if auth is collection-specific
    if auth.collection_ids != '*':
        if not (record := Session.get(Record, record_id)):
            raise HTTPException(HTTP_404_NOT_FOUND)

        if record.collection_id not in auth.collection_ids:
            raise HTTPException(HTTP_403_FORBIDDEN)

    audit_subq = union_all(
        select(
            literal_column("'record'").label('table'),
            null().label('tag_id'),
            RecordAudit.id,
            RecordAudit.client_id,
            RecordAudit.user_id,
            RecordAudit.command,
            RecordAudit.timestamp
        ).where(RecordAudit._id == record_id),
        select(
            literal_column("'record_tag'").label('table'),
            RecordTagAudit._tag_id,
            RecordTagAudit.id,
            RecordTagAudit.client_id,
            RecordTagAudit.user_id,
            RecordTagAudit.command,
            RecordTagAudit.timestamp
        ).where(RecordTagAudit._record_id == record_id)
    ).subquery()

    stmt = (
        select(audit_subq, User.name.label('user_name')).
        outerjoin(User, audit_subq.c.user_id == User.id)
    )

    paginator.sort = 'timestamp'
    return paginator.paginate(
        stmt,
        lambda row: AuditModel(
            table=row.table,
            tag_id=row.tag_id,
            audit_id=row.id,
            client_id=row.client_id,
            user_id=row.user_id,
            user_name=row.user_name,
            command=row.command,
            timestamp=row.timestamp.isoformat(),
        ),
    )


@router.get(
    '/{record_id}/record_audit/{record_audit_id}',
    response_model=RecordAuditModel,
)
async def get_record_audit_detail(
        record_id: str,
        record_audit_id: int,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_READ)),
):
    # allow retrieving the audit detail for a deleted record,
    # except if auth is collection-specific
    if auth.collection_ids != '*':
        if not (record := Session.get(Record, record_id)):
            raise HTTPException(HTTP_404_NOT_FOUND)

        if record.collection_id not in auth.collection_ids:
            raise HTTPException(HTTP_403_FORBIDDEN)

    if not (row := Session.execute(
        select(RecordAudit, User.name.label('user_name')).
        outerjoin(User, RecordAudit.user_id == User.id).
        where(RecordAudit.id == record_audit_id).
        where(RecordAudit._id == record_id)
    ).one_or_none()):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return RecordAuditModel(
        table='record',
        tag_id=None,
        audit_id=row.RecordAudit.id,
        client_id=row.RecordAudit.client_id,
        user_id=row.RecordAudit.user_id,
        user_name=row.user_name,
        command=row.RecordAudit.command,
        timestamp=row.RecordAudit.timestamp.isoformat(),
        record_id=row.RecordAudit._id,
        record_doi=row.RecordAudit._doi,
        record_sid=row.RecordAudit._sid,
        record_metadata=row.RecordAudit._metadata,
        record_collection_id=row.RecordAudit._collection_id,
        record_schema_id=row.RecordAudit._schema_id,
    )


@router.get(
    '/{record_id}/record_tag_audit/{record_tag_audit_id}',
    response_model=RecordTagAuditModel,
)
async def get_record_tag_audit_detail(
        record_id: str,
        record_tag_audit_id: int,
        auth: Authorized = Depends(Authorize(ODPScope.RECORD_READ)),
):
    # allow retrieving the audit detail for a deleted record,
    # except if auth is collection-specific
    if auth.collection_ids != '*':
        if not (record := Session.get(Record, record_id)):
            raise HTTPException(HTTP_404_NOT_FOUND)

        if record.collection_id not in auth.collection_ids:
            raise HTTPException(HTTP_403_FORBIDDEN)

    audit_user_alias = aliased(User)
    tag_user_alias = aliased(User)

    if not (row := Session.execute(
        select(
            RecordTagAudit,
            audit_user_alias.name.label('audit_user_name'),
            tag_user_alias.name.label('tag_user_name')
        ).
        outerjoin(audit_user_alias, RecordTagAudit.user_id == audit_user_alias.id).
        outerjoin(tag_user_alias, RecordTagAudit._user_id == tag_user_alias.id).
        where(RecordTagAudit.id == record_tag_audit_id).
        where(RecordTagAudit._record_id == record_id)
    ).one_or_none()):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return RecordTagAuditModel(
        table='record_tag',
        tag_id=row.RecordTagAudit._tag_id,
        audit_id=row.RecordTagAudit.id,
        client_id=row.RecordTagAudit.client_id,
        user_id=row.RecordTagAudit.user_id,
        user_name=row.audit_user_name,
        command=row.RecordTagAudit.command,
        timestamp=row.RecordTagAudit.timestamp.isoformat(),
        record_tag_id=row.RecordTagAudit._id,
        record_tag_record_id=row.RecordTagAudit._record_id,
        record_tag_user_id=row.RecordTagAudit._user_id,
        record_tag_user_name=row.tag_user_name,
        record_tag_data=row.RecordTagAudit._data,
    )
