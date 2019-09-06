from fastapi import APIRouter, Depends

from ..lib.adapters import ODPAPIAdapter, get_adapter
from ..lib.security import HydraAuth
from ..models.doi import NewDOI

router = APIRouter()


@router.get('/new', response_model=NewDOI,
            summary='Get New SAEON DOI')
async def get_new_saeon_doi(
        adapter: ODPAPIAdapter = Depends(get_adapter),
        access_token: str = Depends(HydraAuth(['SAEON.DOI'])),
):
    return adapter.get_new_saeon_doi(access_token)
