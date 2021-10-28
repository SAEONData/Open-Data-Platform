from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp.api2.models import RoleModel, RoleSort
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import Role

router = APIRouter()


@router.get(
    '/',
    response_model=List[RoleModel],
)
async def list_roles(
        pager: Pager = Depends(Paging(RoleSort)),
):
    stmt = (
        select(Role).
        order_by(getattr(Role, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    roles = [
        RoleModel(
            id=row.Role.id,
            name=row.Role.name,
        )
        for row in Session.execute(stmt)
    ]

    return roles


@router.get(
    '/{role_id}',
    response_model=RoleModel,
)
async def get_role(
        role_id: str,
):
    if not (role := Session.get(Role, role_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return RoleModel(
        id=role.id,
        name=role.name,
    )


@router.post(
    '/',
)
async def create_role(
        role_in: RoleModel,
):
    if Session.get(Role, role_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    role = Role(
        id=role_in.id,
        name=role_in.name,
    )
    role.save()


@router.put(
    '/',
)
async def update_role(
        role_in: RoleModel,
):
    if not (role := Session.get(Role, role_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    role.name = role_in.name
    role.save()


@router.delete(
    '/{role_id}',
)
async def delete_role(
        role_id: str,
):
    if not (role := Session.get(Role, role_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    role.delete()
