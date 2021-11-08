from typing import List

from fastapi import APIRouter, Depends
from jschon import URI
from sqlalchemy import select

from odp import ODPScope
from odp.api2.models import SchemaModel, SchemaSort
from odp.api2.routers import Pager, Paging, Authorize
from odp.db import Session
from odp.db.models import Schema

router = APIRouter()


@router.get(
    '/',
    response_model=List[SchemaModel],
    dependencies=[Depends(Authorize(ODPScope.SCHEMA_READ))],
)
async def list_schemas(
        pager: Pager = Depends(Paging(SchemaSort)),
):
    from odp.api2 import catalog

    stmt = (
        select(Schema).
        order_by(getattr(Schema, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    schemas = [
        SchemaModel(
            id=row.Schema.id,
            type=row.Schema.type,
            uri=row.Schema.uri,
            schema_=catalog.get_schema(URI(row.Schema.uri)).value,
        )
        for row in Session.execute(stmt)
    ]

    return schemas
