from typing import Dict, Any, List, Optional

from pydantic import BaseModel, UUID4, Field


class CatalogueRecord(BaseModel):
    id: UUID4
    doi: Optional[str]
    institution: str
    collection: str
    projects: List[str]
    metadata: Dict[str, Any]


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
