from typing import Dict, List, Any

from pydantic import BaseModel, Field

from odp.api.models import KEY_REGEX


class MetadataSchemaAttributeMapping(BaseModel):
    record_attr: str
    json_path: str
    is_key: bool


class MetadataSchemaIn(BaseModel):
    key: str = Field(..., regex=KEY_REGEX)
    name: str
    schema_: Dict[str, Any] = Field(..., alias='schema')
    template: Dict[str, Any]
    attr_mappings: List[MetadataSchemaAttributeMapping]


class MetadataSchema(BaseModel):
    key: str
    name: str
    schema_: Dict[str, Any] = Field(..., alias='schema')
