from typing import List
from fastapi import APIRouter, Depends, Body

from odpapi.lib.metadata import MetadataRecordsFilter
from odpapi.lib.common import PagerParams
from odpapi.lib.adapter import ODPAPIAdapter, get_adapter
from odpapi.models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataRecordOut,
    MetadataValidationResult,
    MetadataWorkflowResult,
)

router = APIRouter()


@router.get('/', response_model=List[MetadataRecord])
async def list_metadata_records(
        filter: MetadataRecordsFilter = Depends(),
        pager: PagerParams = Depends(),
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.list_metadata_records(filter, pager)


@router.get('/{id_or_doi:path}', response_model=MetadataRecord)
async def get_metadata_record(
        id_or_doi: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.get_metadata_record(id_or_doi)


@router.post('/', response_model=MetadataRecordOut)
async def create_or_update_metadata_record(
        metadata_record: MetadataRecordIn,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.create_or_update_metadata_record(metadata_record)


@router.put('/{id_or_doi:path}', response_model=MetadataRecordOut)
async def update_metadata_record(
        id_or_doi: str,
        metadata_record: MetadataRecordIn,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.update_metadata_record(id_or_doi, metadata_record)


@router.delete('/{id_or_doi:path}', response_model=bool)
async def delete_metadata_record(
        id_or_doi: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.delete_metadata_record(id_or_doi)


@router.post('/validate/{id_or_doi:path}', response_model=MetadataValidationResult)
async def validate_metadata_record(
        id_or_doi: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.validate_metadata_record(id_or_doi)


@router.post('/workflow/{id_or_doi:path}', response_model=MetadataWorkflowResult)
async def set_workflow_state_of_metadata_record(
        id_or_doi: str,
        workflow_state: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
):
    return adapter.set_workflow_state_of_metadata_record(id_or_doi, workflow_state)
