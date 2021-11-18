from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN

from odp import ODPScope
from odp.api2.models import RoleModel, RoleSort
from odp.api2.routers import Pager, Paging, Authorize, Authorized
from odp.db import Session
from odp.db.models import Role, Scope

router = APIRouter()


@router.get(
    '/',
    response_model=List[RoleModel],
)
async def list_roles(
        pager: Pager = Depends(Paging(RoleSort)),
        auth: Authorized = Depends(Authorize(ODPScope.ROLE_READ)),
):
    stmt = (
        select(Role).
        order_by(getattr(Role, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )
    if auth.provider_ids != '*':
        stmt = stmt.where(Role.provider_id.in_(auth.provider_ids))

    roles = [
        RoleModel(
            id=row.Role.id,
            scope_ids=[scope.id for scope in row.Role.scopes],
            provider_id=row.Role.provider_id,
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
        auth: Authorized = Depends(Authorize(ODPScope.ROLE_READ)),
):
    if not (role := Session.get(Role, role_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and role.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    return RoleModel(
        id=role.id,
        scope_ids=[scope.id for scope in role.scopes],
        provider_id=role.provider_id,
    )


@router.post(
    '/',
)
async def create_role(
        role_in: RoleModel,
        auth: Authorized = Depends(Authorize(ODPScope.ROLE_ADMIN)),
):
    if auth.provider_ids != '*' and role_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.get(Role, role_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    role = Role(
        id=role_in.id,
        scopes=[
            Session.get(Scope, scope_id)
            for scope_id in role_in.scope_ids
        ],
        provider_id=role_in.provider_id,
    )
    role.save()


@router.put(
    '/',
)
async def update_role(
        role_in: RoleModel,
        auth: Authorized = Depends(Authorize(ODPScope.ROLE_ADMIN)),
):
    if auth.provider_ids != '*' and role_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (role := Session.get(Role, role_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    role.scopes = [
        Session.get(Scope, scope_id)
        for scope_id in role_in.scope_ids
    ]
    role.provider_id = role_in.provider_id,
    role.save()


@router.delete(
    '/{role_id}',
)
async def delete_role(
        role_id: str,
        auth: Authorized = Depends(Authorize(ODPScope.ROLE_ADMIN)),
):
    if not (role := Session.get(Role, role_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if auth.provider_ids != '*' and role.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    role.delete()
