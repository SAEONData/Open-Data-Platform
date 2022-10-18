from fastapi import APIRouter, Depends, HTTPException
from jschon import URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.models import SchemaModel
from odp.db import Session
from odp.db.models import Schema, SchemaType
from odp.lib.schema import schema_catalog
from odplib.const import ODPScope

router = APIRouter()


@router.get(
    '/',
    response_model=Page[SchemaModel],
    dependencies=[Depends(Authorize(ODPScope.SCHEMA_READ))],
)
async def list_schemas(
        schema_type: SchemaType = None,
        paginator: Paginator = Depends(),
):
    stmt = select(Schema)
    if schema_type:
        stmt = stmt.where(Schema.type == schema_type)

    return paginator.paginate(
        stmt,
        lambda row: SchemaModel(
            id=row.Schema.id,
            type=row.Schema.type,
            uri=row.Schema.uri,
            schema_=schema_catalog.get_schema(URI(row.Schema.uri)).value,
        )
    )


@router.get(
    '/{schema_id}',
    response_model=SchemaModel,
    dependencies=[Depends(Authorize(ODPScope.SCHEMA_READ))],
)
async def get_schema(
        schema_id: str,
):
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
