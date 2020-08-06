from typing import List

from pydantic import BaseModel, Field

from odp.api.models import KEY_REGEX

COLLECTION_SUFFIX = '-collection'
DOI_SCOPE_REGEX = r'^[-._;()/:a-zA-Z0-9]*$'


class CollectionIn(BaseModel):
    key: str = Field(..., regex=KEY_REGEX)
    name: str
    description: str = None
    doi_scope: str = Field('', regex=DOI_SCOPE_REGEX)
    project_keys: List[str] = []


class Collection(BaseModel):
    institution_key: str
    key: str
    name: str
    description: str
    doi_scope: str
    project_keys: List[str]
