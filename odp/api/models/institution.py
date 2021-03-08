from typing import Optional, List

from pydantic import BaseModel, Field

from odp.api.models import KEY_REGEX


class Institution(BaseModel):
    key: str = Field(..., regex=KEY_REGEX)
    name: str
    parent_key: Optional[str] = ...
    domain_names: List[str]
