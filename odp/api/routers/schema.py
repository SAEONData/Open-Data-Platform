from typing import List

from fastapi import APIRouter, Depends, HTTPException
from jschon import URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api.models import SchemaModel, SchemaSort
from odp.api.routers import Pager, Paging, Authorize
from odp.db import Session
from odp.db.models import Schema, SchemaType

router = APIRouter()


@router.get(
    '/',
    response_model=List[SchemaModel],
    dependencies=[Depends(Authorize(ODPScope.SCHEMA_READ))],
)
async def list_schemas(
        schema_type: SchemaType = None,
        pager: Pager = Depends(Paging(SchemaSort)),
):
    from odp.api import schema_catalog

    stmt = (
        select(Schema).
        order_by(getattr(Schema, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )
    if schema_type:
        stmt = stmt.where(Schema.type == schema_type)

    schemas = [
        SchemaModel(
            id=row.Schema.id,
            type=row.Schema.type,
            uri=row.Schema.uri,
            schema_=schema_catalog.get_schema(URI(row.Schema.uri)).value,
        )
        for row in Session.execute(stmt)
    ]

    return schemas


@router.get(
    '/{schema_id}',
    response_model=SchemaModel,
    dependencies=[Depends(Authorize(ODPScope.SCHEMA_READ))],
)
async def get_schema(
        schema_id: str,
):
    from odp.api import schema_catalog

    schema = Session.execute(
        select(Schema).
        where(Schema.id == schema_id)
    ).scalar_one_or_none()

    if not schema:
        raise HTTPException(HTTP_404_NOT_FOUND)

    return SchemaModel(
        id=schema.id,
        type=schema.type,
        uri=schema.uri,
        schema_=schema_catalog.get_schema(URI(schema.uri)).value,
    )
