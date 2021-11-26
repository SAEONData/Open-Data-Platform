from typing import List

from fastapi import APIRouter, Depends, Body, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_404_NOT_FOUND

from odp.api_old.dependencies.auth import Authorizer
from odp.api_old.dependencies.catalogue import get_metadata_landing_page_url
from odp.api_old.models import Pagination
from odp.api_old.models.auth import Role, Scope
from odp.api_old.models.catalogue import CatalogueRecord
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
    '/count',
    response_model=int,
    dependencies=[Depends(Authorizer(Scope.CATALOGUE, Role.HARVESTER))],
)
async def count_catalogue_records(
        institution_key: str = Query(None, description='optional filter on institution key'),
        include_unpublished: bool = Query(False, description=
            'True to count records that are no longer publicly visible'),
):
    return catalogue.count_catalogue_records(institution_key, include_unpublished)


@router.get(
    '/{record_id}',
    response_model=CatalogueRecord,
    dependencies=[Depends(Authorizer(Scope.CATALOGUE, Role.HARVESTER))],
)
async def get_catalogue_record(record_id: str):
    if record := catalogue.get_catalogue_record(record_id):
        return record

    raise HTTPException(HTTP_404_NOT_FOUND)


@router.get(
    '/doi/{doi:path}',
    response_model=CatalogueRecord,
    dependencies=[Depends(Authorizer(Scope.CATALOGUE, Role.HARVESTER))],
)
async def get_catalogue_record_by_doi(doi: str):
    if record := catalogue.get_catalogue_record_by_doi(doi):
        return record

    raise HTTPException(HTTP_404_NOT_FOUND)


@router.get(
    '/sid/{sid:path}',
    response_model=CatalogueRecord,
    dependencies=[Depends(Authorizer(Scope.CATALOGUE, Role.HARVESTER))],
)
async def get_catalogue_record_by_sid(sid: str):
    if record := catalogue.get_catalogue_record_by_sid(sid):
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