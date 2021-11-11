from typing import List

from fastapi import APIRouter, Depends, HTTPException
from jschon import URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api2.models import CatalogueModel, CatalogueSort
from odp.api2.routers import Pager, Paging, Authorize
from odp.db import Session
from odp.db.models import Catalogue

router = APIRouter()


@router.get(
    '/',
    response_model=List[CatalogueModel],
    dependencies=[Depends(Authorize(ODPScope.CATALOGUE_READ))],
)
async def list_catalogues(
        pager: Pager = Depends(Paging(CatalogueSort)),
):
    from odp.api2 import catalog

    stmt = (
        select(Catalogue).
        order_by(getattr(Catalogue, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    catalogues = [
        CatalogueModel(
            id=row.Catalogue.id,
            schema_id=row.Catalogue.schema_id,
            schema_=catalog.get_schema(URI(row.Catalogue.schema.uri)).value,
        )
        for row in Session.execute(stmt)
    ]

    return catalogues


@router.get(
    '/{catalogue_id}',
    response_model=CatalogueModel,
    dependencies=[Depends(Authorize(ODPScope.CATALOGUE_READ))],
)
async def get_catalogue(
        catalogue_id: str,
):
    from odp.api2 import catalog

    if not (catalogue := Session.get(Catalogue, catalogue_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return CatalogueModel(
        id=catalogue.id,
        schema_id=catalogue.schema_id,
        schema_=catalog.get_schema(URI(catalogue.schema.uri)).value,
    )
