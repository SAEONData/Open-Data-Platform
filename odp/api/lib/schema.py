from pathlib import Path

from fastapi import HTTPException
from jschon import JSONSchema, LocalSource, URI, create_catalog
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from odp.api.models import FlagInstanceModelIn, RecordModelIn, TagInstanceModelIn
from odp.db import Session
from odp.db.models import Flag, Schema, SchemaType, Tag

schema_catalog = create_catalog('2020-12', 'translation')
schema_catalog.add_uri_source(
    URI('https://odp.saeon.ac.za/schema/'),
    LocalSource(Path(__file__).parent.parent.parent.parent / 'schema', suffix='.json'),
)


async def get_flag_schema(flag_instance_in: FlagInstanceModelIn) -> JSONSchema:
    if not (flag := Session.get(Flag, flag_instance_in.flag_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid flag id')

    schema = Session.get(Schema, (flag.schema_id, SchemaType.flag))
    return schema_catalog.get_schema(URI(schema.uri))


async def get_tag_schema(tag_instance_in: TagInstanceModelIn) -> JSONSchema:
    if not (tag := Session.get(Tag, tag_instance_in.tag_id)):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    schema = Session.get(Schema, (tag.schema_id, SchemaType.tag))
    return schema_catalog.get_schema(URI(schema.uri))


async def get_metadata_schema(record_in: RecordModelIn) -> JSONSchema:
    if not (schema := Session.get(Schema, (record_in.schema_id, SchemaType.metadata))):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid schema id')

    return schema_catalog.get_schema(URI(schema.uri))
