from typing import Optional

from pydantic import BaseModel, Field

from odp.api.models import KEY_REGEX


class Project(BaseModel):
    key: str = Field(..., regex=KEY_REGEX)
    name: str
    description: Optional[str]
