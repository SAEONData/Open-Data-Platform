from typing import List

from pydantic import BaseModel


class ProjectIn(BaseModel):
    key: str
    name: str


class ProjectOut(BaseModel):
    key: str
    name: str
    role_ids: List[str]
    collection_keys: List[str]
