from typing import List

from fastapi import APIRouter, Depends

from odp.api.dependencies.auth import Authorizer, AuthData
from odp.api.dependencies.ckan import get_ckan_client
from odp.api.models.auth import Role, Scope
from odp.api.models.collection import Collection, CollectionIn
from odp.lib.ckan import CKANClient

router = APIRouter()


@router.get('/', response_model=List[Collection])
async def list_metadata_collections(
        institution_key: str,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, *Role.all())),
):
    return ckan.list_collections(
        institution_key, auth_data.access_token)


@router.post('/', response_model=Collection)
async def create_metadata_collection(
        institution_key: str,
        collection: CollectionIn,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return ckan.create_collection(
        institution_key, collection, auth_data.access_token)
