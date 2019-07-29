from typing import List
from fastapi import APIRouter, Depends

from odpapi.lib.common import PagerParams
from odpapi.lib.adapters import ODPAPIAdapter, get_adapter
from odpapi.models.institution import Institution, InstitutionIn, InstitutionOut

router = APIRouter()


@router.get('/', response_model=List[Institution])
async def list_institutions(
        pager: PagerParams = Depends(),
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.list_institutions(pager)


@router.get('/{id_or_name}', response_model=Institution)
async def get_institution(
        id_or_name: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.get_institution(id_or_name)


@router.post('/', response_model=InstitutionOut)
async def add_institution(
        institution: InstitutionIn,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.add_institution(institution)


@router.put('/{id_or_name}', response_model=InstitutionOut)
async def update_institution(
        id_or_name: str,
        institution: InstitutionIn,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.update_institution(id_or_name, institution)


@router.delete('/{id_or_name}', response_model=bool)
async def delete_institution(
        id_or_name: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.delete_institution(id_or_name)
