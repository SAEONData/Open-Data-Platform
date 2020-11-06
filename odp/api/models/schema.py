from typing import Dict, Any

from pydantic import BaseModel, Field

from odp.api.models import KEY_REGEX


class MetadataSchemaIn(BaseModel):
    key: str = Field(..., regex=KEY_REGEX)
    name: str
    schema_: Dict[str, Any] = Field(..., alias='schema')
    template: Dict[str, Any]
    attr_mappings: Dict[str, str]  # CKAN record attr <- JSON path; e.g. {"title": "/title"}


class MetadataSchema(BaseModel):
    key: str
    name: str
    schema_: Dict[str, Any] = Field(..., alias='schema')
