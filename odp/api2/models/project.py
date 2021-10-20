from enum import Enum
from typing import List

from pydantic import BaseModel


class ProjectModel(BaseModel):
    id: str
    name: str
    collection_ids: List[str]


class ProjectSort(str, Enum):
    ID = 'id'
    NAME = 'name'
