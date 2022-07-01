import re
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, BaseModel, Field, root_validator, validator

from odp.db.models import TagCardinality
from odp.lib.formats import DOI_REGEX, ID_REGEX, SID_REGEX
from odp.lib.hydra import GrantType, ResponseType, TokenEndpointAuthMethod


# Note: reordering models alphabetically with the help of
# `from __future__ import annotations` causes Pydantic to not
# fully instantiate forward ref'd fields, which breaks stuff.


class TagInstanceModel(BaseModel):
    id: str
    tag_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    data: Dict[str, Any]
    timestamp: str
    cardinality: TagCardinality
    public: bool


class TagInstanceModelIn(BaseModel):
    tag_id: str
    data: Dict[str, Any]


class CatalogModel(BaseModel):
    id: str
    schema_id: str
    schema_uri: str
    schema_: Dict[str, Any]


class PublishedTagInstanceModel(BaseModel):
    tag_id: str
    data: Dict[str, Any]
    user_name: Optional[str]
    timestamp: str
    cardinality: TagCardinality


class PublishedRecordModel(BaseModel):
    id: str
    doi: Optional[str]
    sid: Optional[str]
    provider_id: str
    collection_id: str
    project_ids: List[str]
    schema_id: str
    metadata: Dict[str, Any]
    timestamp: str
    tags: List[PublishedTagInstanceModel]


class CatalogRecordModel(BaseModel):
    catalog_id: str
    record_id: str
    timestamp: str
    validity: Dict[str, Any]
    published: bool
    published_record: Optional[PublishedRecordModel]


class ClientModel(BaseModel):
    id: str
    name: str
    scope_ids: List[str]
    collection_id: Optional[str]
    grant_types: List[GrantType]
    response_types: List[ResponseType]
    redirect_uris: List[AnyHttpUrl]
    post_logout_redirect_uris: List[AnyHttpUrl]
    token_endpoint_auth_method: TokenEndpointAuthMethod
    allowed_cors_origins: List[AnyHttpUrl]


class ClientModelIn(ClientModel):
    id: str = Field(..., regex=ID_REGEX)
    secret: str = Field(None, min_length=6)


class CollectionModel(BaseModel):
    id: str
    name: str
    doi_key: Optional[str]
    provider_id: str
    project_ids: List[str]
    record_count: int
    tags: List[TagInstanceModel]
    client_ids: List[str]
    role_ids: List[str]


class CollectionModelIn(BaseModel):
    id: str = Field(..., regex=ID_REGEX)
    name: str
    doi_key: Optional[str]
    provider_id: str


class ProjectModel(BaseModel):
    id: str
    name: str
    collection_ids: List[str]


class ProjectModelIn(BaseModel):
    id: str = Field(..., regex=ID_REGEX)
    name: str
    collection_ids: List[str]


class ProviderModel(BaseModel):
    id: str
    name: str
    collection_ids: List[str]


class ProviderModelIn(BaseModel):
    id: str = Field(..., regex=ID_REGEX)
    name: str


class RecordModel(BaseModel):
    id: str
    doi: Optional[str]
    sid: Optional[str]
    provider_id: str
    collection_id: str
    project_ids: List[str]
    schema_id: str
    metadata: Dict[str, Any]
    validity: Dict[str, Any]
    timestamp: str
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
            pass  # ignore: doi validation already failed

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
            pass  # ignore: doi and/or metadata field validation already failed

        return values


class RoleModel(BaseModel):
    id: str
    scope_ids: List[str]
    collection_id: Optional[str]


class RoleModelIn(BaseModel):
    id: str = Field(..., regex=ID_REGEX)
    scope_ids: List[str]
    collection_id: Optional[str]


class SchemaModel(BaseModel):
    id: str
    type: str
    uri: str
    schema_: Dict[str, Any]


class ScopeModel(BaseModel):
    id: str
    type: str


class TagModel(BaseModel):
    id: str
    cardinality: TagCardinality
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
