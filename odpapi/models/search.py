from typing import Dict, Any

from pydantic import BaseModel, UUID4


class QueryDSL(BaseModel):
    query: Dict[str, Any]


class SearchHit(BaseModel):
    metadata: Dict[str, Any]
    institution: str
    collection: str
    id: UUID4
