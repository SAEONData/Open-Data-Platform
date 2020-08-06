from typing import List

from fastapi import APIRouter, Depends, Request

from odp.api.models.auth import Role, Scope
from odp.api.models.collection import Collection, CollectionIn
from odp.api.security import Authorizer, AuthData

router = APIRouter()


@router.get('/', response_model=List[Collection])
async def list_metadata_collections(
        request: Request,
        institution_key: str,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, *Role.all())),
):
    return request.state.adapter.list_collections(
        institution_key, auth_data.access_token)


@router.post('/', response_model=Collection)
async def create_metadata_collection(
        request: Request,
        institution_key: str,
        collection: CollectionIn,
        auth_data: AuthData = Depends(Authorizer(Scope.METADATA, Role.CURATOR)),
):
    return request.state.adapter.create_collection(
        institution_key, collection, auth_data.access_token)
