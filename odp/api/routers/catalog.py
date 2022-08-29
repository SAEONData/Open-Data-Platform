from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.lib.utils import output_published_record_model
from odp.api.models import CatalogModel, PublishedDataCiteRecordModel, PublishedSAEONRecordModel
from odp.db import Session
from odp.db.models import Catalog, CatalogRecord

router = APIRouter()


@router.get(
    '/',
    response_model=Page[CatalogModel],
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def list_catalogs(
        paginator: Paginator = Depends(),
):
    return paginator.paginate(
        select(Catalog),
        lambda row: CatalogModel(
            id=row.Catalog.id,
        )
    )


@router.get(
    '/{catalog_id}',
    response_model=CatalogModel,
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def get_catalog(
        catalog_id: str,
):
    if not (catalog := Session.get(Catalog, catalog_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return CatalogModel(
        id=catalog.id,
    )


@router.get(
    '/{catalog_id}/records',
    response_model=Page[PublishedSAEONRecordModel | PublishedDataCiteRecordModel],
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def list_published_records(
        catalog_id: str,
        paginator: Paginator = Depends(),
):
    if not Session.get(Catalog, catalog_id):
        raise HTTPException(HTTP_404_NOT_FOUND)

    stmt = (
        select(CatalogRecord).
        where(CatalogRecord.catalog_id == catalog_id).
        where(CatalogRecord.published)
    )

    paginator.sort = 'record_id'
    return paginator.paginate(
        stmt,
        lambda row: output_published_record_model(row.CatalogRecord),
    )
