from fastapi import APIRouter, Depends, HTTPException
from jschon import URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.lib.schema import schema_catalog
from odp.api.models import FlagModel
from odp.db import Session
from odp.db.models import Flag

router = APIRouter()


@router.get(
    '/',
    response_model=Page[FlagModel],
    dependencies=[Depends(Authorize(ODPScope.FLAG_READ))],
)
async def list_flags(
        paginator: Paginator = Depends(),
):
    return paginator.paginate(
        select(Flag),
        lambda row: FlagModel(
            id=row.Flag.id,
            public=row.Flag.public,
            scope_id=row.Flag.scope_id,
            schema_id=row.Flag.schema_id,
            schema_uri=row.Flag.schema.uri,
            schema_=schema_catalog.get_schema(URI(row.Flag.schema.uri)).value,
        )
    )


@router.get(
    '/{flag_id}',
    response_model=FlagModel,
    dependencies=[Depends(Authorize(ODPScope.FLAG_READ))],
)
async def get_flag(
        flag_id: str,
):
    flag = Session.execute(
        select(Flag).
        where(Flag.id == flag_id)
    ).scalar_one_or_none()

    if not flag:
        raise HTTPException(HTTP_404_NOT_FOUND)

    return FlagModel(
        id=flag.id,
        public=flag.public,
        scope_id=flag.scope_id,
        schema_id=flag.schema_id,
        schema_uri=flag.schema.uri,
        schema_=schema_catalog.get_schema(URI(flag.schema.uri)).value,
    )
