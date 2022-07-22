from fastapi import HTTPException
from jschon import JSONSchema, URI
from sqlalchemy import select
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from odp.api.models import RecordModelIn, TagInstanceModelIn
from odp.db import Session
from odp.db.models import Schema, SchemaType, Tag, Vocabulary
from odp.lib.schema import schema_catalog


async def get_tag_schema(tag_instance_in: TagInstanceModelIn) -> JSONSchema:
    if not (tag := Session.execute(
            select(Tag).
            where(Tag.id == tag_instance_in.tag_id)
    ).scalar_one_or_none()):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    schema = Session.get(Schema, (tag.schema_id, SchemaType.tag))
    return schema_catalog.get_schema(URI(schema.uri))


async def get_vocabulary_schema(vocabulary_id: str) -> JSONSchema:
    if not (vocabulary := Session.get(Vocabulary, vocabulary_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid vocabulary id')

    schema = Session.get(Schema, (vocabulary.schema_id, SchemaType.vocabulary))
    return schema_catalog.get_schema(URI(schema.uri))


async def get_metadata_schema(record_in: RecordModelIn) -> JSONSchema:
    if not (schema := Session.get(Schema, (record_in.schema_id, SchemaType.metadata))):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid schema id')

    return schema_catalog.get_schema(URI(schema.uri))
