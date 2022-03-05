from fastapi import APIRouter, Depends
from sqlalchemy import select

from odp import ODPScope
from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.models import ScopeModel
from odp.db.models import Scope

router = APIRouter()


@router.get(
    '/',
    response_model=Page[ScopeModel],
    dependencies=[Depends(Authorize(ODPScope.SCOPE_READ))],
)
async def list_scopes(
        paginator: Paginator = Depends(),
):
    return paginator.paginate(
        select(Scope),
        lambda row: ScopeModel(
            id=row.Scope.id,
            type=row.Scope.type,
        )
    )
