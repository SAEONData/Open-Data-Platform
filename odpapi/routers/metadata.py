from typing import List

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..models import PagerParams
from ..models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataValidationResult,
    MetadataWorkflowResult,
)
from ..security import Authorizer, AuthData

router = APIRouter()


@router.get('/', response_model=List[MetadataRecord])
async def list_metadata_records(
        request: Request,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer(read_only=True)),
        pager: PagerParams = Depends(),
):
    return request.state.adapter.list_metadata_records(
        institution_key, pager, auth_data.access_token)


@router.get('/{id:path}', response_model=MetadataRecord)
async def get_metadata_record(
        request: Request,
        id: str,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer(read_only=True)),
):
    return request.state.adapter.get_metadata_record(
        id, auth_data.access_token)


@router.post('/', response_model=MetadataRecord)
async def create_or_update_metadata_record(
        request: Request,
        metadata_record: MetadataRecordIn,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer()),
):
    return request.state.adapter.create_or_update_metadata_record(
        metadata_record, auth_data.access_token)


@router.put('/{id:path}', response_model=MetadataRecord)
async def update_metadata_record(
        request: Request,
        id: str,
        metadata_record: MetadataRecordIn,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer()),
):
    return request.state.adapter.update_metadata_record(
        id, metadata_record, auth_data.access_token)


@router.delete('/{id:path}', response_model=bool)
async def delete_metadata_record(
        request: Request,
        id: str,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer()),
):
    return request.state.adapter.delete_metadata_record(
        id, auth_data.access_token)


@router.post('/validate/{id:path}', response_model=MetadataValidationResult)
async def validate_metadata_record(
        request: Request,
        id: str,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer()),
):
    return request.state.adapter.validate_metadata_record(
        id, auth_data.access_token)


@router.post('/workflow/{id:path}', response_model=MetadataWorkflowResult)
async def set_workflow_state_of_metadata_record(
        request: Request,
        id: str,
        workflow_state: str,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer(admin_only=True)),
):
    return request.state.adapter.set_workflow_state_of_metadata_record(
        id, workflow_state, auth_data.access_token)
