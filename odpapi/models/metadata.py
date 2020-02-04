from typing import Dict, Optional
from pydantic import BaseModel, Field, UUID4

# adapted from https://www.crossref.org/blog/dois-and-matching-regular-expressions
DOI_REGEX = r'^10\.\d{4,}(\.\d+)*/[-._;()/:a-zA-Z0-9]+$'


class MetadataRecordIn(BaseModel):
    institution: str
    collection: str
    metadata_standard: str
    metadata: Dict
    doi: str = Field('', regex=DOI_REGEX)
    auto_assign_doi: bool = False


class MetadataRecord(BaseModel):
    id: UUID4
    pid: Optional[str]
    doi: str
    institution: str
    collection: str
    metadata_standard: str
    metadata: Dict
    state: str
    errors: Dict
    validated: bool
    workflow_state: Optional[str]


class MetadataValidationResult(BaseModel):
    success: bool
    errors: Dict


class MetadataWorkflowResult(BaseModel):
    success: bool
    errors: Dict
