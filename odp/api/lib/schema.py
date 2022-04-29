import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException
from jschon import JSONSchema, LocalSource, URI, create_catalog
from jschon.translation import translation_filter
from sqlalchemy import select
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
    if not (flag := Session.execute(
            select(Flag).
            where(Flag.id == flag_instance_in.flag_id)
    ).scalar_one_or_none()):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid flag id')

    schema = Session.get(Schema, (flag.schema_id, SchemaType.flag))
    return schema_catalog.get_schema(URI(schema.uri))


async def get_tag_schema(tag_instance_in: TagInstanceModelIn) -> JSONSchema:
    if not (tag := Session.execute(
            select(Tag).
            where(Tag.id == tag_instance_in.tag_id)
    ).scalar_one_or_none()):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid tag id')

    schema = Session.get(Schema, (tag.schema_id, SchemaType.tag))
    return schema_catalog.get_schema(URI(schema.uri))


async def get_metadata_schema(record_in: RecordModelIn) -> JSONSchema:
    if not (schema := Session.get(Schema, (record_in.schema_id, SchemaType.metadata))):
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid schema id')

    return schema_catalog.get_schema(URI(schema.uri))


@translation_filter('date-to-year')
def date_to_year(date: str) -> int:
    return datetime.strptime(date, '%Y-%m-%d').year


@translation_filter('base-url')
def base_url(url: str) -> str:
    u = urlparse(url)
    return f'{u.scheme}://{u.netloc}'


@translation_filter('split-archived-formats')
def split_archived_formats(value: str) -> list:
    """Filter for translating /onlineResources/n/applicationProfile (iso19115-saeon)
    to /immutableResource/resourceDownload/archivedFormats (datacite4-saeon).

    e.g. given "[shp, shx, dbf]", return ["shp", "shx", "dbf"]
    """
    if not re.match("^\\[\\s*\\w+\\s*(,\\s*\\w+\\s*)*]$", value):
        raise ValueError('Invalid input for split-archived-formats filter')
    return [item.strip() for item in value[1:-1].split(',')]
