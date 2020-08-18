import os
from typing import List

from fastapi import APIRouter, Depends, Request

from odp.api.models.auth import Role, Scope
from odp.api.models.project import Project
from odp.api.security import Authorizer, AuthData

router = APIRouter()


@router.get('/', response_model=List[Project])
async def list_projects(
        request: Request,
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            *Role.all(),
            institution_key=os.environ['ADMIN_INSTITUTION'])),
):
    return request.state.adapter.list_projects(auth_data.access_token)


@router.post('/', response_model=Project)
async def create_or_update_project(
        request: Request,
        project: Project,
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            Role.ADMIN,
            institution_key=os.environ['ADMIN_INSTITUTION'])),
):
    return request.state.adapter.create_or_update_project(project, auth_data.access_token)
