from fastapi import APIRouter, Depends
from sqlalchemy import select

from odp.api.lib.auth import Authorize
from odp.api.lib.paging import Page, Paginator
from odp.api.models import ScopeModel
from odp.db.models import Scope
from odplib.const import ODPScope

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
        ),
        custom_sort="array_position(array['openid'], id),"
                    "array_position(array['oauth','odp','client'], type::text),"
                    "id"
    )
