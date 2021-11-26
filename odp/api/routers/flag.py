from typing import List

from fastapi import APIRouter, Depends, HTTPException
from jschon import URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api.models import FlagModel, FlagSort
from odp.api.routers import Pager, Paging, Authorize
from odp.db import Session
from odp.db.models import Flag

router = APIRouter()


@router.get(
    '/',
    response_model=List[FlagModel],
    dependencies=[Depends(Authorize(ODPScope.FLAG_READ))],
)
async def list_flags(
        pager: Pager = Depends(Paging(FlagSort)),
):
    from odp.api import schema_catalog

    stmt = (
        select(Flag).
        order_by(getattr(Flag, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    flags = [
        FlagModel(
            id=row.Flag.id,
            public=row.Flag.public,
            scope_id=row.Flag.scope_id,
            schema_id=row.Flag.schema_id,
            schema_uri=row.Flag.schema.uri,
            schema_=schema_catalog.get_schema(URI(row.Flag.schema.uri)).value,
        )
        for row in Session.execute(stmt)
    ]

    return flags


@router.get(
    '/{flag_id}',
    response_model=FlagModel,
    dependencies=[Depends(Authorize(ODPScope.FLAG_READ))],
)
async def get_flag(
        flag_id: str,
):
    from odp.api import schema_catalog

    if not (flag := Session.get(Flag, flag_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return FlagModel(
        id=flag.id,
        public=flag.public,
        scope_id=flag.scope_id,
        schema_id=flag.schema_id,
        schema_uri=flag.schema.uri,
        schema_=schema_catalog.get_schema(URI(flag.schema.uri)).value,
    )
