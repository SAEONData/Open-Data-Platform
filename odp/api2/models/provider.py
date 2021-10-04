from enum import Enum
from typing import List

from pydantic import BaseModel


class ProviderIn(BaseModel):
    id: str
    name: str


class ProviderOut(BaseModel):
    id: str
    name: str
    role_ids: List[str]
    collection_ids: List[str]


class ProviderSort(str, Enum):
    ID = 'id'
    NAME = 'name'
