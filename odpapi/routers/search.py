from typing import List, Dict

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..models import PagerParams
from ..models.search import SearchParams

router = APIRouter()


@router.get('/', response_model=List[Dict])
async def search_metadata(
        request: Request,
        search_params: SearchParams = Depends(),
        pager_params: PagerParams = Depends(),
):
    search_terms = {k: v for k, v in request.query_params.items() if
                    k not in search_params.__dict__.keys() | pager_params.__dict__.keys()}
    results = await request.state.adapter.search_metadata(search_params, pager_params, **search_terms)
    return results
