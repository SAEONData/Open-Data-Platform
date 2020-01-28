from typing import List

from pydantic import BaseModel


class TokenIn(BaseModel):
    token: str
    require_scope: List[str]
    require_audience: List[str] = None
