from typing import List

from fastapi import APIRouter, Depends, Request
from odp.api.models.auth import Role, Scope
from odp.api.models import Pagination
from odp.api.models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataValidationResult,
    MetadataWorkflowResult,
)
from odp.api.security import Authorizer, AuthData

router = APIRouter()


@router.get('/', response_model=List[MetadataRecord])
async def list_metadata_records(
        request: Request,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, *Role.all())),
        pagination: Pagination = Depends(),
):
    return request.state.adapter.list_metadata_records(
        institution_key, pagination, auth_data.access_token)


@router.get('/{record_id:path}', response_model=MetadataRecord)
async def get_metadata_record(
        request: Request,
        institution_key: str,
        record_id: str,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, *Role.all())),
):
    return request.state.adapter.get_metadata_record(
        institution_key, record_id, auth_data.access_token)


@router.post('/', response_model=MetadataRecord)
async def create_or_update_metadata_record(
        request: Request,
        institution_key: str,
        metadata_record: MetadataRecordIn,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR, Role.CONTRIBUTOR)),
):
    return request.state.adapter.create_or_update_metadata_record(
        institution_key, metadata_record, auth_data.access_token)


@router.put('/{record_id:path}', response_model=MetadataRecord)
async def update_metadata_record(
        request: Request,
        institution_key: str,
        record_id: str,
        metadata_record: MetadataRecordIn,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return request.state.adapter.update_metadata_record(
        institution_key, record_id, metadata_record, auth_data.access_token)


@router.delete('/{record_id:path}', response_model=bool)
async def delete_metadata_record(
        request: Request,
        institution_key: str,
        record_id: str,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return request.state.adapter.delete_metadata_record(
        institution_key, record_id, auth_data.access_token)


@router.post('/validate/{record_id:path}', response_model=MetadataValidationResult)
async def validate_metadata_record(
        request: Request,
        institution_key: str,
        record_id: str,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return request.state.adapter.validate_metadata_record(
        institution_key, record_id, auth_data.access_token)


@router.post('/workflow/{record_id:path}', response_model=MetadataWorkflowResult)
async def change_state_of_metadata_record(
        request: Request,
        institution_key: str,
        record_id: str,
        state: str,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return request.state.adapter.change_state_of_metadata_record(
        institution_key, record_id, state, auth_data.access_token)
