from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from odp.api2.models import ScopeIn, ScopeOut, ScopeSort
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import Scope

router = APIRouter()


@router.get('/', response_model=List[ScopeOut])
async def list_scopes(
        pager: Pager = Depends(Paging(ScopeSort)),
):
    stmt = (
        select(Scope).
        order_by(getattr(Scope, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    scopes = [
        ScopeOut(
            id=row.Scope.id,
        )
        for row in Session.execute(stmt)
    ]

    return scopes


@router.get('/{scope_id}', response_model=ScopeOut)
async def get_scope(
        scope_id: str,
):
    if not (scope := Session.get(Scope, scope_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return ScopeOut(
        id=scope.id,
    )


@router.post('/')
async def create_scope(
        scope_in: ScopeIn,
):
    if Session.get(Scope, scope_in.id):
        raise HTTPException(HTTP_409_CONFLICT)

    scope = Scope(
        id=scope_in.id,
    )
    scope.save()


@router.delete('/{scope_id}')
async def delete_scope(
        scope_id: str,
):
    if not (scope := Session.get(Scope, scope_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    scope.delete()
