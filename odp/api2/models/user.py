from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class UserIn(BaseModel):
    id: str
    active: bool


class UserOut(BaseModel):
    id: str
    email: str
    active: bool
    verified: bool
    name: str
    picture: Optional[str]
    role_ids: List[str]


class UserSort(str, Enum):
    NAME = 'name'
    EMAIL = 'email'
