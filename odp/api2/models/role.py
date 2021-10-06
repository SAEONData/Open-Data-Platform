from enum import Enum

from pydantic import BaseModel


class RoleIn(BaseModel):
    id: str
    name: str


class RoleOut(BaseModel):
    id: str
    name: str


class RoleSort(str, Enum):
    ID = 'id'
    NAME = 'name'
