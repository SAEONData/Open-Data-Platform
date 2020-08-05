from typing import Optional

from pydantic import BaseModel, Field

from odp.api.models import KEY_REGEX

PROJECT_SUFFIX = '-project'


class Project(BaseModel):
    key: str = Field(..., regex=KEY_REGEX)
    name: str
    description: Optional[str]
