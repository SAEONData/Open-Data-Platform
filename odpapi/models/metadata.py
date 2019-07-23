from typing import Set, Dict
from pydantic import BaseModel, Schema, UUID4

from odpapi.lib.metadata import DOI_REGEX


class MetadataRecordIn(BaseModel):
    institution: str
    collection: str = Schema(None, description="If not specified, the institution's default metadata collection will be used.")
    metadata_standard: str
    metadata: Dict
    infrastructures: Set[str]


class MetadataRecordOut(BaseModel):
    id: UUID4
    doi: str = Schema(None, regex=DOI_REGEX)
    state: str
    errors: Dict
    validated: bool
    workflow_state: str = None


class MetadataRecord(MetadataRecordIn, MetadataRecordOut):
    pass


class MetadataValidationResult(BaseModel):
    success: bool
    errors: Dict


class MetadataWorkflowResult(BaseModel):
    success: bool
    errors: Dict
