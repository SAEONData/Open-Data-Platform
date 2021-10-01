from typing import List

from pydantic import BaseModel


class CollectionIn(BaseModel):
    key: str
    name: str
    provider_key: str


class CollectionOut(BaseModel):
    key: str
    name: str
    provider_key: str
    project_keys: List[str]
    record_count: int
