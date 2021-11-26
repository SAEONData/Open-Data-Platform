from typing import List

from fastapi import APIRouter, Depends, HTTPException
from jschon import URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api.models import TagModel, TagSort
from odp.api.routers import Pager, Paging, Authorize
from odp.db import Session
from odp.db.models import Tag

router = APIRouter()


@router.get(
    '/',
    response_model=List[TagModel],
    dependencies=[Depends(Authorize(ODPScope.TAG_READ))],
)
async def list_tags(
        pager: Pager = Depends(Paging(TagSort)),
):
    from odp.api import schema_catalog

    stmt = (
        select(Tag).
        order_by(getattr(Tag, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    tags = [
        TagModel(
            id=row.Tag.id,
            public=row.Tag.public,
            scope_id=row.Tag.scope_id,
            schema_id=row.Tag.schema_id,
            schema_uri=row.Tag.schema.uri,
            schema_=schema_catalog.get_schema(URI(row.Tag.schema.uri)).value,
        )
        for row in Session.execute(stmt)
    ]

    return tags


@router.get(
    '/{tag_id}',
    response_model=TagModel,
    dependencies=[Depends(Authorize(ODPScope.TAG_READ))],
)
async def get_tag(
        tag_id: str,
):
    from odp.api import schema_catalog

    if not (tag := Session.get(Tag, tag_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return TagModel(
        id=tag.id,
        public=tag.public,
        scope_id=tag.scope_id,
        schema_id=tag.schema_id,
        schema_uri=tag.schema.uri,
        schema_=schema_catalog.get_schema(URI(tag.schema.uri)).value,
    )