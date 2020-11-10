import re
from enum import Enum
from typing import Dict, Optional, Any

from pydantic import BaseModel, Field, UUID4, AnyHttpUrl, validator

# adapted from https://www.crossref.org/blog/dois-and-matching-regular-expressions
DOI_REGEX = r'^10\.\d{4,}(\.\d+)*/[-._;()/:a-zA-Z0-9]+$'

# the suffix part of the DOI regex suffices for secondary IDs
SID_REGEX = r'^[-._;()/:a-zA-Z0-9]+$'


class MetadataRecordIn(BaseModel):
    doi: str = Field(None, regex=DOI_REGEX, description="Digital Object Identifier (DOI)")
    sid: str = Field(None, regex=SID_REGEX, description="Secondary Identifier; mandatory if DOI is not given")
    collection_key: str
    schema_key: str
    metadata: Dict[str, Any]

    @validator('sid', always=True)
    def validate_sid(cls, sid, values):
        try:
            if not values['doi'] and not sid:
                raise ValueError("A secondary ID is mandatory if a DOI is not given")
        except KeyError:
            pass  # doi validation failed

        if sid and re.match(DOI_REGEX, sid):
            raise ValueError("The secondary ID cannot be a DOI")

        return sid


class MetadataRecord(BaseModel):
    id: UUID4
    doi: Optional[str]
    sid: Optional[str]
    institution_key: str
    collection_key: str
    schema_key: str
    metadata: Dict[str, Any]
    validated: bool
    errors: Dict
    state: Optional[str]


class MetadataValidationResult(BaseModel):
    success: bool
    errors: Dict


class MetadataWorkflowResult(BaseModel):
    success: bool
    errors: Dict
