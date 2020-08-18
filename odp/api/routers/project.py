import os
from typing import List

from fastapi import APIRouter, Depends

from odp.api.dependencies.auth import Authorizer, AuthData
from odp.api.dependencies.ckan import get_ckan_client
from odp.api.models.auth import Role, Scope
from odp.api.models.project import Project
from odp.lib.ckan import CKANClient

router = APIRouter()


@router.get('/', response_model=List[Project])
async def list_projects(
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            *Role.all(),
            institution_key=os.environ['ADMIN_INSTITUTION'])),
):
    return ckan.list_projects(auth_data.access_token)


@router.post('/', response_model=Project)
async def create_or_update_project(
        project: Project,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            Role.ADMIN,
            institution_key=os.environ['ADMIN_INSTITUTION'])),
):
    return ckan.create_or_update_project(project, auth_data.access_token)
