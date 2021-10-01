from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, func

from odp.api2.models import CollectionOut
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import Collection, Record

router = APIRouter()


@router.get('/', response_model=List[CollectionOut])
async def list_collections(pager: Pager = Depends(Paging('key', 'name'))):
    stmt = (
        select(Collection, func.count(Record.id)).
        outerjoin(Record).
        group_by(Collection).
        order_by(getattr(Collection, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    collections = [
        CollectionOut(
            key=row.Collection.key,
            name=row.Collection.name,
            provider_key=row.Collection.provider.key,
            project_keys=[project.key for project in row.Collection.projects],
            record_count=row.count,
        )
        for row in Session.execute(stmt)
    ]

    return collections
