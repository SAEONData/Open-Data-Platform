from fastapi import APIRouter, Depends
from starlette.requests import Request

from odp.api.models import Pagination
from odp.api.models.search import QueryDSL, SearchResult

router = APIRouter()


@router.post('/', response_model=SearchResult)
async def search_metadata(
        request: Request,
        query_dsl: QueryDSL,
        pagination: Pagination = Depends(),
):
    result = await request.state.adapter.search_metadata(query_dsl, pagination)
    return result
