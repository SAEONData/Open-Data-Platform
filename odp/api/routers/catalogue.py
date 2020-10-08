from typing import List

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_404_NOT_FOUND

from odp.api.dependencies.catalogue import get_metadata_landing_page_url
from odp.api.models import Pagination
from odp.api.models.catalogue import CatalogueRecord
from odp.lib import catalogue

router = APIRouter()


@router.get('/', response_model=List[CatalogueRecord])
async def list_catalogue_records(pagination: Pagination = Depends()):
    return catalogue.list_catalogue_records(pagination)


@router.get('/{record_id}', response_model=CatalogueRecord)
async def get_catalogue_record(record_id: str):
    if record := catalogue.get_catalogue_record(record_id):
        return record

    raise HTTPException(HTTP_404_NOT_FOUND)


@router.get('/go/{record_id}')
async def go_to_catalogue_record(
        redirect_url: str = Depends(get_metadata_landing_page_url),
):
    return RedirectResponse(redirect_url)
