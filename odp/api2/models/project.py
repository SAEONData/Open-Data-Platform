from enum import Enum
from typing import List

from pydantic import BaseModel


class ProjectIn(BaseModel):
    id: str
    name: str


class ProjectOut(BaseModel):
    id: str
    name: str
    role_ids: List[str]
    collection_ids: List[str]


class ProjectSort(str, Enum):
    ID = 'id'
    NAME = 'name'
