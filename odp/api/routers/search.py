from fastapi import APIRouter, Depends

from odp.api.dependencies.elastic import get_elastic_client
from odp.api.models import Pagination
from odp.api.models.search import QueryDSL, SearchResult
from odp.lib.elastic import ElasticClient

router = APIRouter()


@router.post('/', response_model=SearchResult)
async def search_metadata(
        query_dsl: QueryDSL,
        pagination: Pagination = Depends(),
        elastic: ElasticClient = Depends(get_elastic_client),
):
    result = await elastic.search_metadata(query_dsl, pagination)
    return result
