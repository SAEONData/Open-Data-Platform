from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from odp import ODPScope
from odp.api.lib.auth import Authorize
from odp.api.models import ScopeModel
from odp.db import Session
from odp.db.models import Scope

router = APIRouter()


@router.get(
    '/',
    response_model=List[ScopeModel],
    dependencies=[Depends(Authorize(ODPScope.SCOPE_READ))],
)
async def list_scopes():
    stmt = (
        select(Scope).
        order_by(Scope.id)
    )

    scopes = [
        ScopeModel(
            id=row.Scope.id,
        )
        for row in Session.execute(stmt)
    ]

    return scopes
