from dataclasses import dataclass

from fastapi import HTTPException


@dataclass
class Pager:
    sort: str
    skip: int
    limit: int


class Paging:
    def __init__(self, sort_enum):
        self.sort_keys = [e.value for e in sort_enum]

    def __call__(self, sort: str = None, skip: int = 0, limit: int = 100) -> Pager:
        if sort and sort not in self.sort_keys:
            raise HTTPException(422, f'Sort key must be one of {self.sort_keys}')
        sort = sort or self.sort_keys[0]
        return Pager(sort=sort, skip=skip, limit=limit)