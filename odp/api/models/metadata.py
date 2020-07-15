from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field, UUID4, AnyHttpUrl

# adapted from https://www.crossref.org/blog/dois-and-matching-regular-expressions
# Note: this allows either a DOI string or an empty string
DOI_REGEX = r'^(|10\.\d{4,}(\.\d+)*/[-._;()/:a-zA-Z0-9]+)$'


class CaptureMethod(str, Enum):
    WIZARD = 'wizard'
    HARVESTER = 'harvester'


class MetadataRecordIn(BaseModel):
    collection_key: str
    schema_key: str
    metadata: Dict
    doi: str = Field('', regex=DOI_REGEX)
    auto_assign_doi: bool = False
    terms_conditions_accepted: bool
    data_agreement_accepted: bool
    data_agreement_url: AnyHttpUrl
    capture_method: CaptureMethod


class MetadataRecord(BaseModel):
    id: UUID4
    pid: Optional[str]
    doi: str
    institution_key: str
    collection_key: str
    schema_key: str
    metadata: Dict
    validated: bool
    errors: Dict
    state: Optional[str]


class MetadataValidationResult(BaseModel):
    success: bool
    errors: Dict


class MetadataWorkflowResult(BaseModel):
    success: bool
    errors: Dict
