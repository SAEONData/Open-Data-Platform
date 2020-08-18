from typing import List

from fastapi import APIRouter, Depends

from odp.api.dependencies.auth import Authorizer, AuthData
from odp.api.dependencies.ckan import get_ckan_client
from odp.api.models import Pagination
from odp.api.models.auth import Role, Scope
from odp.api.models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataValidationResult,
    MetadataWorkflowResult,
)
from odp.lib.ckan import CKANClient

router = APIRouter()


@router.get('/', response_model=List[MetadataRecord])
async def list_metadata_records(
        institution_key: str,
        pagination: Pagination = Depends(),
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, *Role.all())),
):
    return ckan.list_metadata_records(
        institution_key, pagination, auth_data.access_token)


@router.get('/{record_id:path}', response_model=MetadataRecord)
async def get_metadata_record(
        institution_key: str,
        record_id: str,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, *Role.all())),
):
    return ckan.get_metadata_record(
        institution_key, record_id, auth_data.access_token)


@router.post('/', response_model=MetadataRecord)
async def create_or_update_metadata_record(
        institution_key: str,
        metadata_record: MetadataRecordIn,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR, Role.CONTRIBUTOR)),
):
    return ckan.create_or_update_metadata_record(
        institution_key, metadata_record, auth_data.access_token)


@router.put('/{record_id:path}', response_model=MetadataRecord)
async def update_metadata_record(
        institution_key: str,
        record_id: str,
        metadata_record: MetadataRecordIn,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return ckan.update_metadata_record(
        institution_key, record_id, metadata_record, auth_data.access_token)


@router.delete('/{record_id:path}', response_model=bool)
async def delete_metadata_record(
        institution_key: str,
        record_id: str,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return ckan.delete_metadata_record(
        institution_key, record_id, auth_data.access_token)


@router.post('/validate/{record_id:path}', response_model=MetadataValidationResult)
async def validate_metadata_record(
        institution_key: str,
        record_id: str,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return ckan.validate_metadata_record(
        institution_key, record_id, auth_data.access_token)


@router.post('/workflow/{record_id:path}', response_model=MetadataWorkflowResult)
async def change_state_of_metadata_record(
        institution_key: str,
        record_id: str,
        state: str,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return ckan.change_state_of_metadata_record(
        institution_key, record_id, state, auth_data.access_token)
