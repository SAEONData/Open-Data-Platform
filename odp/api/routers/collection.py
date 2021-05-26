from typing import List

from fastapi import APIRouter, Depends

from odp.api.dependencies.auth import InstitutionalResourceAuthorizer, AuthData
from odp.api.dependencies.ckan import get_ckan_client
from odp.api.models.auth import Role, Scope
from odp.api.models.collection import Collection, CollectionIn
from odp.lib.ckan import CKANClient
from odp.lib.institutions import get_institution

router = APIRouter()


@router.get('/', response_model=List[Collection])
async def list_metadata_collections(
        institution_key: str,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(InstitutionalResourceAuthorizer(
            Scope.METADATA,
            *Role.all())),
):
    return ckan.list_collections(
        institution_key, auth_data.access_token)


@router.post('/', response_model=Collection)
async def create_or_update_metadata_collection(
        institution_key: str,
        collection: CollectionIn,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(InstitutionalResourceAuthorizer(
            Scope.METADATA,
            Role.CURATOR)),
):
    # institution = get_institution(institution_key)
    # ckan.create_or_update_institution(institution, auth_data.access_token)
    return ckan.create_or_update_collection(
        institution_key, collection, auth_data.access_token)
