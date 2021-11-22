from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException

from odp.api_old.dependencies.auth import Authorizer
from odp.api_old.dependencies.datacite import get_datacite_client
from odp.api_old.models.auth import Role, Scope
from odp.api_old.models.datacite import DataciteRecordIn, DataciteRecord, DataciteRecordList
from odp.lib.datacite import DataciteClient
from odp.lib.exceptions import DataciteError

router = APIRouter()


@router.get(
    '/',
    response_model=DataciteRecordList,
    dependencies=[Depends(Authorizer(
        Scope.METADATA,
        Role.ADMIN, Role.CURATOR,
    ))],
    summary="List DOIs",
)
async def list_dois(
        page_size: int = Query(default=20, ge=1, le=1000),
        page_num: int = Query(default=1, ge=1),
        datacite: DataciteClient = Depends(get_datacite_client),
):
    try:
        return datacite.list_dois(page_size, page_num)
    except DataciteError as e:
        raise HTTPException(e.status_code, e.error_detail) from e


@router.get(
    '/{doi:path}',
    response_model=DataciteRecord,
    dependencies=[Depends(Authorizer(
        Scope.METADATA,
        Role.ADMIN, Role.CURATOR,
    ))],
    summary="Get DOI",
)
async def get_doi(
        doi: str,
        datacite: DataciteClient = Depends(get_datacite_client),
):
    try:
        return datacite.get_doi(doi)
    except DataciteError as e:
        raise HTTPException(e.status_code, e.error_detail) from e


@router.post(
    '/',
    response_model=DataciteRecord,
    dependencies=[Depends(Authorizer(
        Scope.METADATA,
        Role.ADMIN, Role.CURATOR,
    ))],
    summary="Publish DOI",
)
async def publish_doi(
        record: DataciteRecordIn,
        datacite: DataciteClient = Depends(get_datacite_client),
):
    try:
        return datacite.publish_doi(record)
    except DataciteError as e:
        raise HTTPException(e.status_code, e.error_detail) from e


@router.delete(
    '/{doi:path}',
    dependencies=[Depends(Authorizer(
        Scope.METADATA,
        Role.ADMIN, Role.CURATOR,
    ))],
    summary="Un-publish DOI",
)
async def unpublish_doi(
        doi: str,
        datacite: DataciteClient = Depends(get_datacite_client),
):
    try:
        datacite.unpublish_doi(doi)
    except DataciteError as e:
        raise HTTPException(e.status_code, e.error_detail) from e
