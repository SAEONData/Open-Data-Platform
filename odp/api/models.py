import re
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator, root_validator

from odp.lib.formats import DOI_REGEX, SID_REGEX


class FlagInstanceModel(BaseModel):
    flag_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime


class FlagInstanceModelIn(BaseModel):
    flag_id: str
    data: Dict[str, Any]


class TagInstanceModel(BaseModel):
    tag_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime


class TagInstanceModelIn(BaseModel):
    tag_id: str
    data: Dict[str, Any]


class CatalogueModel(BaseModel):
    id: str
    schema_id: str
    schema_uri: str
    schema_: Dict[str, Any]


class ClientModel(BaseModel):
    id: str
    name: str
    scope_ids: List[str]
    provider_id: Optional[str]


class CollectionModel(BaseModel):
    id: str
    name: str
    doi_key: Optional[str]
    provider_id: str
    project_ids: List[str]
    record_count: int
    flags: List[FlagInstanceModel]
    tags: List[TagInstanceModel]


class CollectionModelIn(BaseModel):
    id: str
    name: str
    doi_key: Optional[str]
    provider_id: str


class FlagModel(BaseModel):
    id: str
    public: bool
    scope_id: str
    schema_id: str
    schema_uri: str
    schema_: Dict[str, Any]


class ProjectModel(BaseModel):
    id: str
    name: str
    collection_ids: List[str]


class ProviderModel(BaseModel):
    id: str
    name: str
    collection_ids: List[str]
    client_ids: List[str]
    role_ids: List[str]


class ProviderModelIn(BaseModel):
    id: str
    name: str


class RecordModel(BaseModel):
    id: str
    doi: Optional[str]
    sid: Optional[str]
    collection_id: str
    schema_id: str
    metadata: Dict[str, Any]
    validity: Dict[str, Any]
    timestamp: datetime
    flags: List[FlagInstanceModel]
    tags: List[TagInstanceModel]


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

    @root_validator
    def set_metadata_doi(cls, values):
        """Copy the DOI into the metadata post-validation."""
        try:
            if doi := values['doi']:
                values['metadata']['doi'] = doi
            else:
                values['metadata'].pop('doi', None)
        except KeyError:
            pass  # field validation failed

        return values


class RoleModel(BaseModel):
    id: str
    scope_ids: List[str]
    provider_id: Optional[str]


class SchemaModel(BaseModel):
    id: str
    type: str
    uri: str
    schema_: Dict[str, Any]


class ScopeModel(BaseModel):
    id: str


class TagModel(BaseModel):
    id: str
    public: bool
    scope_id: str
    schema_id: str
    schema_uri: str
    schema_: Dict[str, Any]


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
