from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field
from pydantic.networks import AnyHttpUrl

from odp.api.models.metadata import DOI_REGEX


class DataciteRecordIn(BaseModel):
    doi: str = Field(..., regex=DOI_REGEX)
    url: AnyHttpUrl = Field(..., description="The metadata landing page in the ODP")
    metadata: Dict[str, Any]


class DataciteRecord(BaseModel):
    doi: str
    url: Optional[AnyHttpUrl]
    metadata: Dict[str, Any]


class DataciteRecordList(BaseModel):
    total_records: int
    total_pages: int
    this_page: int
    records: List[DataciteRecord]
