from typing import List

from fastapi import APIRouter, Depends, Body, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_404_NOT_FOUND

from odp.api.dependencies.auth import Authorizer
from odp.api.dependencies.catalogue import get_metadata_landing_page_url
from odp.api.models import Pagination
from odp.api.models.auth import Role, Scope
from odp.api.models.catalogue import CatalogueRecord
from odp.lib import catalogue

router = APIRouter()


@router.get(
    '/',
    response_model=List[CatalogueRecord],
    dependencies=[Depends(Authorizer(Scope.CATALOGUE, Role.HARVESTER))],
)
async def list_catalogue_records(
        institution_key: str = Query(None, description='optional filter on institution key'),
        include_unpublished: bool = Query(False, description=
            'True to include records that are no longer publicly visible, to '
            'facilitate local deletion by a client; if included, these records '
            'will only contain the `id` and `published` (set to `False`) fields'),
        pagination: Pagination = Depends(),
):
    return catalogue.list_catalogue_records(institution_key, include_unpublished, pagination)


@router.get(
    '/{record_id}',
    response_model=CatalogueRecord,
    dependencies=[Depends(Authorizer(Scope.CATALOGUE, Role.HARVESTER))],
)
async def get_catalogue_record(record_id: str):
    if record := catalogue.get_catalogue_record(record_id):
        return record

    raise HTTPException(HTTP_404_NOT_FOUND)


@router.post(
    '/',
    response_model=List[CatalogueRecord],
    dependencies=[Depends(Authorizer(Scope.CATALOGUE, Role.HARVESTER))],
)
async def select_catalogue_records(
        ids: List[str] = Body(...),
        pagination: Pagination = Depends(),
):
    return catalogue.select_catalogue_records(ids, pagination)


@router.get('/go/{record_id_or_doi:path}')
async def go_to_catalogue_record(
        redirect_url: str = Depends(get_metadata_landing_page_url),
):
    return RedirectResponse(redirect_url)
