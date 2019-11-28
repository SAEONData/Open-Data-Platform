from typing import Set, Dict, Optional
from pydantic import BaseModel, Schema, UUID4

from ..lib.metadata import DOI_REGEX


class MetadataRecordIn(BaseModel):
    institution: str
    collection: str = Schema(None, description="If not specified, the institution's default metadata collection will be used.")
    metadata_standard: str
    metadata: Dict
    infrastructures: Set[str]
    doi: str = Schema('', regex=DOI_REGEX)
    auto_assign_doi: bool = False


class MetadataRecord(BaseModel):
    id: UUID4
    doi: str
    institution: str
    collection: str
    metadata_standard: str
    metadata: Dict
    infrastructures: Set[str]
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
