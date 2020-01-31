from typing import List

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..lib.metadata import MetadataRecordsFilter
from ..lib.common import PagerParams
from ..models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataValidationResult,
    MetadataWorkflowResult,
)

router = APIRouter()


@router.get('/', response_model=List[MetadataRecord])
async def list_metadata_records(
        request: Request,
        filter: MetadataRecordsFilter = Depends(),
        pager: PagerParams = Depends(),
):
    return request.state.adapter.list_metadata_records(
        filter, pager, request.state.access_token)


@router.get('/{id:path}', response_model=MetadataRecord)
async def get_metadata_record(
        request: Request,
        id: str,
):
    return request.state.adapter.get_metadata_record(
        id, request.state.access_token)


@router.post('/', response_model=MetadataRecord)
async def create_or_update_metadata_record(
        request: Request,
        metadata_record: MetadataRecordIn,
):
    return request.state.adapter.create_or_update_metadata_record(
        metadata_record, request.state.access_token)


@router.put('/{id:path}', response_model=MetadataRecord)
async def update_metadata_record(
        request: Request,
        id: str,
        metadata_record: MetadataRecordIn,
):
    return request.state.adapter.update_metadata_record(
        id, metadata_record, request.state.access_token)


@router.delete('/{id:path}', response_model=bool)
async def delete_metadata_record(
        request: Request,
        id: str,
):
    return request.state.adapter.delete_metadata_record(
        id, request.state.access_token)


@router.post('/validate/{id:path}', response_model=MetadataValidationResult)
async def validate_metadata_record(
        request: Request,
        id: str,
):
    return request.state.adapter.validate_metadata_record(
        id, request.state.access_token)


@router.post('/workflow/{id:path}', response_model=MetadataWorkflowResult)
async def set_workflow_state_of_metadata_record(
        request: Request,
        id: str,
        workflow_state: str,
):
    return request.state.adapter.set_workflow_state_of_metadata_record(
        id, workflow_state, request.state.access_token)
