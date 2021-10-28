from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class ClientModel(BaseModel):
    id: str
    name: str
    scope_ids: List[str]


class ClientSort(str, Enum):
    ID = 'id'
    NAME = 'name'


class CollectionModel(BaseModel):
    id: str
    name: str
    provider_id: str
    project_ids: List[str]
    record_count: int


class CollectionModelIn(BaseModel):
    id: str
    name: str
    provider_id: str


class CollectionSort(str, Enum):
    ID = 'id'
    NAME = 'name'
    PROVIDER_ID = 'provider_id'


class ProjectModel(BaseModel):
    id: str
    name: str
    collection_ids: List[str]


class ProjectSort(str, Enum):
    ID = 'id'
    NAME = 'name'


class ProviderModel(BaseModel):
    id: str
    name: str
    collection_ids: List[str]
    client_ids: List[str]
    role_ids: List[str]


class ProviderModelIn(BaseModel):
    id: str
    name: str


class ProviderSort(str, Enum):
    ID = 'id'
    NAME = 'name'


class RoleModel(BaseModel):
    id: str
    name: str
    scope_ids: List[str]


class RoleSort(str, Enum):
    ID = 'id'
    NAME = 'name'


class ScopeModel(BaseModel):
    id: str


class ScopeSort(str, Enum):
    ID = 'id'


class UserModel(BaseModel):
    id: str
    email: str
    active: bool
    verified: bool
    name: str
    picture: Optional[str]
    role_ids: List[str]


class UserModelIn(BaseModel):
    id: str
    active: bool
    role_ids: List[str]


class UserSort(str, Enum):
    NAME = 'name'
    EMAIL = 'email'
