from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from odp.api.dependencies.catalogue import get_metadata_landing_page_url
from odp.api.dependencies.elastic import get_elastic_client
from odp.api.models import Pagination
from odp.api.models.catalogue import QueryDSL, SearchResult, CatalogueRecord
from odp.lib.elastic import ElasticClient

router = APIRouter()


@router.post('/query', response_model=SearchResult)
async def query_catalogue(
        query_dsl: QueryDSL,
        pagination: Pagination = Depends(),
        elastic: ElasticClient = Depends(get_elastic_client),
):
    result = await elastic.query(query_dsl, pagination)
    return result


@router.get('/get/', response_model=List[CatalogueRecord])
async def list_catalogue_records(
        pagination: Pagination = Depends(),
        elastic: ElasticClient = Depends(get_elastic_client),
):
    result = await elastic.list_records(pagination)
    return result


@router.get('/get/{record_id}', response_model=CatalogueRecord)
async def get_catalogue_record(
        record_id: str,
        elastic: ElasticClient = Depends(get_elastic_client),
):
    result = await elastic.get_record(record_id)
    return result


@router.get('/go/{record_id}')
async def go_to_catalogue_record(
        redirect_url: str = Depends(get_metadata_landing_page_url),
):
    return RedirectResponse(redirect_url)
