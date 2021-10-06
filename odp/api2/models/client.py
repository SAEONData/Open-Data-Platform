from enum import Enum

from pydantic import BaseModel


class ClientIn(BaseModel):
    id: str
    name: str


class ClientOut(BaseModel):
    id: str
    name: str


class ClientSort(str, Enum):
    ID = 'id'
    NAME = 'name'
