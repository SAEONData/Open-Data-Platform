from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from odp import ODPScope
from odp.api.models import ScopeModel, ScopeSort
from odp.api.routers import Pager, Paging, Authorize
from odp.db import Session
from odp.db.models import Scope

router = APIRouter()


@router.get(
    '/',
    response_model=List[ScopeModel],
    dependencies=[Depends(Authorize(ODPScope.SCOPE_READ))],
)
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
        ScopeModel(
            id=row.Scope.id,
        )
        for row in Session.execute(stmt)
    ]

    return scopes
