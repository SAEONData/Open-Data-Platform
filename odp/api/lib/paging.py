from math import ceil
from typing import Callable, Generic, List, TypeVar

from fastapi import HTTPException, Query
from pydantic import BaseModel
from pydantic.generics import GenericModel
from sqlalchemy import func, select
from sqlalchemy.engine import Row
from sqlalchemy.exc import CompileError
from sqlalchemy.sql import Select
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from odp.db import Base, Session

ModelT = TypeVar('ModelT', bound=BaseModel)


class Page(GenericModel, Generic[ModelT]):
    items: List[ModelT]
    total: int
    page: int
    pages: int


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
            sort_model: Base = None,
    ) -> Page[ModelT]:
        total = Session.execute(
            select(func.count()).
            select_from(query.subquery())
        ).scalar_one()

        try:
            sort_col = getattr(sort_model, self.sort) if sort_model else self.sort
            items = [
                item_factory(row) for row in Session.execute(
                    query.
                    order_by(sort_col).
                    offset(self.size * (self.page - 1)).
                    limit(self.size)
                )
            ]
        except (AttributeError, CompileError):
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid sort column')

        return Page(
            items=items,
            total=total,
            page=self.page,
            pages=ceil(total / self.size),
        )
