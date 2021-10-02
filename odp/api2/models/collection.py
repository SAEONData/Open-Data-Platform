from enum import Enum
from typing import List

from pydantic import BaseModel


class CollectionIn(BaseModel):
    id: str
    name: str
    provider_id: str


class CollectionOut(BaseModel):
    id: str
    name: str
    provider_id: str
    project_ids: List[str]
    record_count: int


class CollectionSort(str, Enum):
    ID = 'id'
    NAME = 'name'
    PROVIDER_ID = 'provider_id'
