from enum import Enum

from pydantic import BaseModel


class ScopeIn(BaseModel):
    id: str


class ScopeOut(BaseModel):
    id: str


class ScopeSort(str, Enum):
    ID = 'id'
