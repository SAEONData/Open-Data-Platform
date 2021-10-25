from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp import ODPScope
from odp.api2.models import ProjectModel, ProjectSort
from odp.api2.routers import Pager, Paging, Authorize
from odp.db import Session
from odp.db.models import Project, Collection

router = APIRouter()


@router.get(
    '/',
    response_model=List[ProjectModel],
    dependencies=[Depends(Authorize(ODPScope.PROJECT_READ))],
)
async def list_projects(
        pager: Pager = Depends(Paging(ProjectSort)),
):
    stmt = (
        select(Project).
        order_by(getattr(Project, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    projects = [
        ProjectModel(
            id=row.Project.id,
            name=row.Project.name,
            collection_ids=[collection.id for collection in row.Project.collections],
        )
        for row in Session.execute(stmt)
    ]

    return projects


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
        project_in: ProjectModel,
):
    if Session.get(Project, project_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

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
        project_in: ProjectModel,
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
