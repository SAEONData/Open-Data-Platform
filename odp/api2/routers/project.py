from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from odp.api2.models import ProjectOut
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import Project

router = APIRouter()


@router.get('/', response_model=List[ProjectOut])
async def list_projects(pager: Pager = Depends(Paging('key', 'name'))):
    stmt = (
        select(Project).
        order_by(getattr(Project, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    projects = [
        ProjectOut(
            key=row.Project.key,
            name=row.Project.name,
            role_ids=[role.id for role in row.Project.roles],
            collection_keys=[collection.key for collection in row.Project.collections],
        )
        for row in Session.execute(stmt)
    ]

    return projects
