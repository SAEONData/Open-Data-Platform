from fastapi import APIRouter, Depends, HTTPException
from jschon import URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.lib.schema import schema_catalog
from odp.api.models import CatalogModel
from odp.db import Session
from odp.db.models import Catalog

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
            schema_id=row.Catalog.schema_id,
            schema_uri=row.Catalog.schema.uri,
            schema_=schema_catalog.get_schema(URI(row.Catalog.schema.uri)).value,
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
        schema_id=catalog.schema_id,
        schema_uri=catalog.schema.uri,
        schema_=schema_catalog.get_schema(URI(catalog.schema.uri)).value,
    )
