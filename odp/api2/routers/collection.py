from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, func

from odp.api2.models import CollectionOut, CollectionSort
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import Collection, Record

router = APIRouter()


@router.get('/', response_model=List[CollectionOut])
async def list_collections(pager: Pager = Depends(Paging(CollectionSort))):
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
            id=row.Collection.id,
            name=row.Collection.name,
            provider_id=row.Collection.provider.id,
            project_ids=[project.id for project in row.Collection.projects],
            record_count=row.count,
        )
        for row in Session.execute(stmt)
    ]

    return collections
