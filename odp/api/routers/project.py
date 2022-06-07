from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp import ODPScope
from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.models import ProjectModel, ProjectModelIn
from odp.db import Session
from odp.db.models import Collection, Project

router = APIRouter()


@router.get(
    '/',
    response_model=Page[ProjectModel],
    dependencies=[Depends(Authorize(ODPScope.PROJECT_READ))],
)
async def list_projects(
        paginator: Paginator = Depends(),
):
    return paginator.paginate(
        select(Project),
        lambda row: ProjectModel(
            id=row.Project.id,
            name=row.Project.name,
            collection_ids=[collection.id for collection in row.Project.collections],
        )
    )


@router.get(
    '/{project_id}',
    response_model=ProjectModel,
    dependencies=[Depends(Authorize(ODPScope.PROJECT_READ))],
)
async def get_project(
        project_id: str,
):
    if not (project := Session.get(Project, project_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return ProjectModel(
        id=project.id,
        name=project.name,
        collection_ids=[collection.id for collection in project.collections],
    )


@router.post(
    '/',
    dependencies=[Depends(Authorize(ODPScope.PROJECT_ADMIN))],
)
async def create_project(
        project_in: ProjectModelIn,
):
    if Session.get(Project, project_in.id):
        raise HTTPException(HTTP_409_CONFLICT, 'Project id is already in use')

    project = Project(
        id=project_in.id,
        name=project_in.name,
        collections=[
            Session.get(Collection, collection_id)
            for collection_id in project_in.collection_ids
        ],
    )
    project.save()


@router.put(
    '/',
    dependencies=[Depends(Authorize(ODPScope.PROJECT_ADMIN))],
)
async def update_project(
        project_in: ProjectModelIn,
):
    if not (project := Session.get(Project, project_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    project.name = project_in.name
    project.collections = [
        Session.get(Collection, collection_id)
        for collection_id in project_in.collection_ids
    ]
    project.save()


@router.delete(
    '/{project_id}',
    dependencies=[Depends(Authorize(ODPScope.PROJECT_ADMIN))],
)
async def delete_project(
        project_id: str,
):
    if not (project := Session.get(Project, project_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    project.delete()
