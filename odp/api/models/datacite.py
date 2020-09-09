from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic.networks import AnyHttpUrl

from odp.api.models.metadata import DOI_REGEX


class DataCiteMetadataIn(BaseModel):
    doi: str = Field(..., regex=DOI_REGEX)
    url: AnyHttpUrl
    metadata: dict


class DataCiteMetadata(BaseModel):
    doi: str
    url: Optional[AnyHttpUrl]
    metadata: dict


class DataCiteMetadataList(BaseModel):
    total_records: int
    total_pages: int
    this_page: int
    records: List[DataCiteMetadata]
