from fastapi import APIRouter, Depends, HTTPException
from jschon import URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp import ODPScope
from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.lib.schema import schema_catalog
from odp.api.models import CatalogueModel
from odp.db import Session
from odp.db.models import Catalogue

router = APIRouter()


@router.get(
    '/',
    response_model=Page[CatalogueModel],
    dependencies=[Depends(Authorize(ODPScope.CATALOGUE_READ))],
)
async def list_catalogues(
        paginator: Paginator = Depends(),
):
    return paginator.paginate(
        select(Catalogue),
        lambda row: CatalogueModel(
            id=row.Catalogue.id,
            schema_id=row.Catalogue.schema_id,
            schema_uri=row.Catalogue.schema.uri,
            schema_=schema_catalog.get_schema(URI(row.Catalogue.schema.uri)).value,
        )
    )


@router.get(
    '/{catalogue_id}',
    response_model=CatalogueModel,
    dependencies=[Depends(Authorize(ODPScope.CATALOGUE_READ))],
)
async def get_catalogue(
        catalogue_id: str,
):
    if not (catalogue := Session.get(Catalogue, catalogue_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return CatalogueModel(
        id=catalogue.id,
        schema_id=catalogue.schema_id,
        schema_uri=catalogue.schema.uri,
        schema_=schema_catalog.get_schema(URI(catalogue.schema.uri)).value,
    )
