import re
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator

from odp.lib.formats import DOI_REGEX, SID_REGEX


class CatalogueModel(BaseModel):
    id: str
    schema_id: str
    schema_uri: str
    schema_: Dict[str, Any]


class CatalogueSort(str, Enum):
    ID = 'id'


class ClientModel(BaseModel):
    id: str
    name: str
    scope_ids: List[str]
    provider_id: Optional[str]


class ClientSort(str, Enum):
    ID = 'id'
    NAME = 'name'


class CollectionFlagModel(BaseModel):
    flag_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime


class CollectionFlagModelIn(BaseModel):
    flag_id: str
    data: Dict[str, Any]


class CollectionTagModel(BaseModel):
    tag_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime


class CollectionTagModelIn(BaseModel):
    tag_id: str
    data: Dict[str, Any]


class CollectionModel(BaseModel):
    id: str
    name: str
    provider_id: str
    project_ids: List[str]
    record_count: int
    flags: List[CollectionFlagModel]
    tags: List[CollectionTagModel]


class CollectionModelIn(BaseModel):
    id: str
    name: str
    provider_id: str


class CollectionSort(str, Enum):
    ID = 'id'
    NAME = 'name'
    PROVIDER_ID = 'provider_id'


class FlagModel(BaseModel):
    id: str
    public: bool
    scope_id: str
    schema_id: str
    schema_uri: str
    schema_: Dict[str, Any]


class FlagSort(str, Enum):
    ID = 'id'


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


class RecordFlagModel(BaseModel):
    flag_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime


class RecordFlagModelIn(BaseModel):
    flag_id: str
    data: Dict[str, Any]


class RecordTagModel(BaseModel):
    tag_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime


class RecordTagModelIn(BaseModel):
    tag_id: str
    data: Dict[str, Any]


class RecordModel(BaseModel):
    id: str
    doi: Optional[str]
    sid: Optional[str]
    collection_id: str
    schema_id: str
    metadata: Dict[str, Any]
    validity: Dict[str, Any]
    timestamp: datetime
    flags: List[RecordFlagModel]
    tags: List[RecordTagModel]


class RecordModelIn(BaseModel):
    doi: str = Field(None, regex=DOI_REGEX, description="Digital Object Identifier")
    sid: str = Field(None, regex=SID_REGEX, description="Secondary Identifier")
    collection_id: str
    schema_id: str
    metadata: Dict[str, Any]

    @validator('sid', always=True)
    def validate_sid(cls, sid, values):
        try:
            if not values['doi'] and not sid:
                raise ValueError("Secondary ID is mandatory if a DOI is not provided")
        except KeyError:
            pass  # doi validation failed

        if sid and re.match(DOI_REGEX, sid):
            raise ValueError("The secondary ID cannot be a DOI")

        return sid


class RecordSort(str, Enum):
    DOI = 'doi'
    SID = 'sid'


class RoleModel(BaseModel):
    id: str
    scope_ids: List[str]
    provider_id: Optional[str]


class RoleSort(str, Enum):
    ID = 'id'


class SchemaModel(BaseModel):
    id: str
    type: str
    uri: str
    schema_: Dict[str, Any]


class SchemaSort(str, Enum):
    ID = 'id'
    TYPE = 'type'


class ScopeModel(BaseModel):
    id: str


class ScopeSort(str, Enum):
    ID = 'id'


class TagModel(BaseModel):
    id: str
    public: bool
    scope_id: str
    schema_id: str
    schema_uri: str
    schema_: Dict[str, Any]


class TagSort(str, Enum):
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
