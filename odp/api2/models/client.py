from enum import Enum
from typing import List

from pydantic import BaseModel


class ClientModel(BaseModel):
    id: str
    name: str
    scope_ids: List[str]


class ClientSort(str, Enum):
    ID = 'id'
    NAME = 'name'
