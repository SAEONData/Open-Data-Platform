from typing import List, Dict

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..models import Pagination
from ..models.search import SearchParams

router = APIRouter()


@router.get('/', response_model=List[Dict])
async def search_metadata(
        request: Request,
        search_params: SearchParams = Depends(),
        pagination: Pagination = Depends(),
):
    search_terms = {k: v for k, v in request.query_params.items() if
                    k not in search_params.__dict__.keys() | pagination.__dict__.keys()}
    results = await request.state.adapter.search_metadata(search_params, pagination, **search_terms)
    return results
