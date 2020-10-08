from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field, validator


class CatalogueRecord(BaseModel):
    """ Model of a metadata record as published to a catalogue.

    This must be strictly JSON-serializable.
    """
    id: str
    doi: Optional[str]
    institution: str
    collection: str
    projects: List[str]
    schema: str
    metadata: Dict[str, Any]
    published: bool

    @validator('projects')
    def normalize_projects_list(cls, v):
        return sorted(set(v))


class QueryDSL(BaseModel):
    query: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "query": {
                    "match_all": {}
                }
            }
        }


class SearchHit(BaseModel):
    score: float
    record: CatalogueRecord


class SearchResult(BaseModel):
    total_hits: int
    max_score: Optional[float]
    query_time: Optional[int] = Field(..., description="Search execution time in milliseconds")
    hits: List[SearchHit]
