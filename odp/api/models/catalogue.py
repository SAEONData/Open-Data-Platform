from typing import Dict, Any, List

from pydantic import BaseModel, Field, validator


class CatalogueRecord(BaseModel):
    """Model representing a metadata record published to the ODP catalogue.

    Records that are later un-published are retained in the catalogue, but
    when harvested will only indicate their ``id`` and ``published`` state.
    """
    # this model must be strictly JSON-serializable,
    # as it is stored to a back-end JSONB column
    id: str
    doi: str = None
    institution: str = None
    collection: str = None
    projects: List[str] = None
    schema_: str = Field(None, alias='schema')
    metadata: Dict[str, Any] = None
    published: bool

    @validator('projects')
    def normalize_projects_list(cls, v):
        if v is not None:
            return sorted(set(v))
        return v
