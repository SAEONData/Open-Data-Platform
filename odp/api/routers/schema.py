from typing import List

from fastapi import APIRouter, Depends

from odp.api.dependencies.auth import Authorizer, AuthData
from odp.api.dependencies.ckan import get_ckan_client
from odp.api.models.auth import Role, Scope
from odp.api.models.schema import MetadataSchema, MetadataSchemaIn
from odp.config import config
from odp.lib.ckan import CKANClient

router = APIRouter()


@router.get('/', response_model=List[MetadataSchema])
async def list_metadata_schemas(
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            *Role.all(),
            institution_key=config.ODP.ADMIN.INSTITUTION)),
):
    return ckan.list_metadata_schemas(auth_data.access_token)


@router.post('/', response_model=MetadataSchema)
async def create_or_update_metadata_schema(
        schema: MetadataSchemaIn,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            Role.ADMIN,
            institution_key=config.ODP.ADMIN.INSTITUTION)),
):
    return ckan.create_or_update_metadata_schema(schema, auth_data.access_token)
