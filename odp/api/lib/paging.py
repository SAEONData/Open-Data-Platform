from dataclasses import dataclass
from typing import Generic, TypeVar, List, Callable

from fastapi import HTTPException, Query
from pydantic import BaseModel
from pydantic.generics import GenericModel
from sqlalchemy import select, func
from sqlalchemy.engine import Row
from sqlalchemy.exc import CompileError
from sqlalchemy.sql import Select
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from odp.db import Session


@dataclass
class Pager:
    sort: str
    skip: int
    limit: int


class Paging:
    def __init__(self, sort_enum):
        self.sort_keys = [e.value for e in sort_enum]

    async def __call__(self, sort: str = None, skip: int = 0, limit: int = 100) -> Pager:
        if sort and sort not in self.sort_keys:
            raise HTTPException(
                HTTP_422_UNPROCESSABLE_ENTITY,
                f'Sort key must be one of {self.sort_keys}',
            )
        sort = sort or self.sort_keys[0]
        return Pager(sort=sort, skip=skip, limit=limit)


ModelT = TypeVar('ModelT', bound=BaseModel)


class Page(GenericModel, Generic[ModelT]):
    items: List[ModelT]
    total: int
    page: int
    size: int


class Paginator:
    def __init__(
            self,
            page: int = Query(1, ge=1, description='Page number'),
            size: int = Query(50, ge=1, description='Page size'),
            sort: str = Query('id', description='Sort column'),
    ):
        self.page = page
        self.size = size
        self.sort = sort

    def paginate(
            self,
            query: Select,
            item_factory: Callable[[Row], ModelT],
    ) -> Page[ModelT]:
        total = Session.execute(
            select(func.count()).
            select_from(query.subquery())
        ).scalar_one()

        try:
            items = [
                item_factory(row) for row in Session.execute(
                    query.
                    order_by(self.sort).
                    offset(self.size * (self.page - 1)).
                    limit(self.size)
                )
            ]
        except CompileError:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid sort column')

        return Page(
            items=items,
            total=total,
            page=self.page,
            size=self.size,
        )
