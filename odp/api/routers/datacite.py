from fastapi import APIRouter, Depends, Query

from odp.api.dependencies.auth import Authorizer
from odp.api.dependencies.datacite import get_datacite_client
from odp.api.models.auth import Role, Scope
from odp.api.models.datacite import DataCiteMetadataIn, DataCiteMetadata, DataCiteMetadataList
from odp.lib.datacite import DataCiteClient

router = APIRouter()


@router.get(
    '/',
    response_model=DataCiteMetadataList,
    dependencies=[Depends(Authorizer(
        Scope.METADATA,
        Role.ADMIN, Role.CURATOR,
    ))],
    summary="List DOIs",
)
async def list_dois(
        page_size: int = Query(default=20, ge=1, le=1000),
        page_num: int = Query(default=1, ge=1),
        datacite: DataCiteClient = Depends(get_datacite_client),
):
    return datacite.list_dois(page_size, page_num)


@router.get(
    '/{doi:path}',
    response_model=DataCiteMetadata,
    dependencies=[Depends(Authorizer(
        Scope.METADATA,
        Role.ADMIN, Role.CURATOR,
    ))],
    summary="Get DOI",
)
async def get_doi(
        doi: str,
        datacite: DataCiteClient = Depends(get_datacite_client),
):
    return datacite.get_doi(doi)


@router.post(
    '/',
    response_model=DataCiteMetadata,
    dependencies=[Depends(Authorizer(
        Scope.METADATA,
        Role.ADMIN, Role.CURATOR,
    ))],
    summary="Publish DOI",
)
async def publish_doi(
        metadata: DataCiteMetadataIn,
        datacite: DataCiteClient = Depends(get_datacite_client),
):
    return datacite.publish_doi(metadata.doi, metadata.url, metadata.metadata)


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
        datacite: DataCiteClient = Depends(get_datacite_client),
):
    datacite.unpublish_doi(doi)
