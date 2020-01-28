from typing import Optional

from pydantic import BaseModel


class Institution(BaseModel):
    key: str
    name: str
    parent_key: Optional[str]
    registry_key: str
