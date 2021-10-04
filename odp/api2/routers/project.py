from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from odp.api2.models import ProjectIn, ProjectOut, ProjectSort
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import Project

router = APIRouter()


@router.get('/', response_model=List[ProjectOut])
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
        ProjectOut(
            id=row.Project.id,
            name=row.Project.name,
            role_ids=[role.id for role in row.Project.roles],
            collection_ids=[collection.id for collection in row.Project.collections],
        )
        for row in Session.execute(stmt)
    ]

    return projects


@router.get('/{project_id}', response_model=ProjectOut)
async def get_project(
        project_id: str,
):
    if not (project := Session.get(Project, project_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return ProjectOut(
        id=project.id,
        name=project.name,
        role_ids=[role.id for role in project.roles],
        collection_ids=[collection.id for collection in project.collections],
    )


@router.post('/')
async def create_project(
        project_in: ProjectIn,
):
    if Session.get(Project, project_in.id):
        raise HTTPException(status.HTTP_409_CONFLICT)

    project = Project(
        id=project_in.id,
        name=project_in.name,
    )
    project.save()


@router.put('/')
async def update_project(
        project_in: ProjectIn,
):
    if not (project := Session.get(Project, project_in.id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    project.name = project_in.name
    project.save()


@router.delete('/{project_id}')
async def delete_project(
        project_id: str,
):
    if not (project := Session.get(Project, project_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    project.delete()
