from typing import List
from fastapi import APIRouter, Depends

from ..lib.metadata import MetadataRecordsFilter
from ..lib.common import PagerParams
from ..lib.adapters import ODPAPIAdapter, get_adapter
from ..lib.security import HydraAuth
from ..models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataValidationResult,
    MetadataWorkflowResult,
)

router = APIRouter()


@router.get('/', response_model=List[MetadataRecord])
async def list_metadata_records(
        filter: MetadataRecordsFilter = Depends(),
        pager: PagerParams = Depends(),
        adapter: ODPAPIAdapter = Depends(get_adapter),
        access_token: str = Depends(HydraAuth(['ODP.Metadata'])),
):
    return adapter.list_metadata_records(filter, pager, access_token)


@router.get('/{id:path}', response_model=MetadataRecord)
async def get_metadata_record(
        id: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
        access_token: str = Depends(HydraAuth(['ODP.Metadata'])),
):
    return adapter.get_metadata_record(id, access_token)


@router.post('/', response_model=MetadataRecord)
async def create_or_update_metadata_record(
        metadata_record: MetadataRecordIn,
        adapter: ODPAPIAdapter = Depends(get_adapter),
        access_token: str = Depends(HydraAuth(['ODP.Metadata'])),
):
    return adapter.create_or_update_metadata_record(metadata_record, access_token)


@router.put('/{id:path}', response_model=MetadataRecord)
async def update_metadata_record(
        id: str,
        metadata_record: MetadataRecordIn,
        adapter: ODPAPIAdapter = Depends(get_adapter),
        access_token: str = Depends(HydraAuth(['ODP.Metadata'])),
):
    return adapter.update_metadata_record(id, metadata_record, access_token)


@router.delete('/{id:path}', response_model=bool)
async def delete_metadata_record(
        id: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
        access_token: str = Depends(HydraAuth(['ODP.Metadata'])),
):
    return adapter.delete_metadata_record(id, access_token)


@router.post('/validate/{id:path}', response_model=MetadataValidationResult)
async def validate_metadata_record(
        id: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
        access_token: str = Depends(HydraAuth(['ODP.Metadata'])),
):
    return adapter.validate_metadata_record(id, access_token)


@router.post('/workflow/{id:path}', response_model=MetadataWorkflowResult)
async def set_workflow_state_of_metadata_record(
        id: str,
        workflow_state: str,
        adapter: ODPAPIAdapter = Depends(get_adapter),
        access_token: str = Depends(HydraAuth(['ODP.Metadata'])),
):
    return adapter.set_workflow_state_of_metadata_record(id, workflow_state, access_token)
