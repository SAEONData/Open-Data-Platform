from typing import Dict, Any, List

from pydantic import BaseModel, UUID4, Field


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
    metadata_id: UUID4
    metadata: Dict[str, Any]


class SearchResult(BaseModel):
    total_hits: int
    max_score: float
    query_time: int = Field(..., description="Search execution time in milliseconds")
    hits: List[SearchHit]
