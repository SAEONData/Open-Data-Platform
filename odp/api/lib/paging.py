from math import ceil
from typing import Callable, Generic, List, TypeVar

from fastapi import HTTPException, Query
from pydantic import BaseModel
from pydantic.generics import GenericModel
from sqlalchemy import func, select, text
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
            size: int = Query(50, ge=0, description='Page size (0 = unlimited)'),
            sort: str = Query('id', description='Sort column'),
    ):
        self.page = page
        self.size = size
        self.sort = sort

    def paginate(
            self,
            query: Select,
            item_factory: Callable[[Row], ModelT],
            *,
            sort_model: Base = None,
            custom_sort: str = None,
    ) -> Page[ModelT]:
        total = Session.execute(
            select(func.count()).
            select_from(query.subquery())
        ).scalar_one()

        try:
            if sort_model:
                sort_col = getattr(sort_model, self.sort)
            elif custom_sort:
                sort_col = text(custom_sort)
            else:
                sort_col = self.sort

            limit = self.size or total

            items = [
                item_factory(row) for row in Session.execute(
                    query.
                    order_by(sort_col).
                    offset(limit * (self.page - 1)).
                    limit(limit)
                )
            ]
        except (AttributeError, CompileError):
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid sort column')

        return Page(
            items=items,
            total=total,
            page=self.page,
            pages=ceil(total / limit) if limit else 0,
        )
