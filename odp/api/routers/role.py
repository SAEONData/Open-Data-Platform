from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp import ODPScope
from odp.api.lib.auth import Authorize, Authorized, select_scopes
from odp.api.lib.paging import Page, Paginator
from odp.api.models import RoleModel, RoleModelIn
from odp.db import Session
from odp.db.models import Role, ScopeType

router = APIRouter()


@router.get(
    '/',
    response_model=Page[RoleModel],
)
async def list_roles(
        auth: Authorized = Depends(Authorize(ODPScope.ROLE_READ)),
        paginator: Paginator = Depends(),
):
    stmt = select(Role)
    if auth.provider_ids != '*':
        stmt = stmt.where(Role.provider_id.in_(auth.provider_ids))

    return paginator.paginate(
        stmt,
        lambda row: RoleModel(
            id=row.Role.id,
            scope_ids=[scope.id for scope in row.Role.scopes],
            provider_id=row.Role.provider_id,
        )
    )


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
        role_in: RoleModelIn,
        auth: Authorized = Depends(Authorize(ODPScope.ROLE_ADMIN)),
):
    if auth.provider_ids != '*' and role_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if Session.get(Role, role_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    role = Role(
        id=role_in.id,
        scopes=select_scopes(role_in.scope_ids, [ScopeType.odp, ScopeType.client]),
        provider_id=role_in.provider_id,
    )
    role.save()


@router.put(
    '/',
)
async def update_role(
        role_in: RoleModelIn,
        auth: Authorized = Depends(Authorize(ODPScope.ROLE_ADMIN)),
):
    if auth.provider_ids != '*' and role_in.provider_id not in auth.provider_ids:
        raise HTTPException(HTTP_403_FORBIDDEN)

    if not (role := Session.get(Role, role_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    role.scopes = select_scopes(role_in.scope_ids, [ScopeType.odp, ScopeType.client])
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
