from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from odp.lib.auth import UserAccess


class TokenUse(str, Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


class ValidToken(BaseModel):
    """ Token introspection response for a valid token """
    active: bool = Field(default=True, const=True)
    token_type: str = Field(default='Bearer', const=True)
    token_use: TokenUse
    client_id: str
    scope: str
    sub: str
    iss: str
    iat: int
    exp: int
    nbf: Optional[int]
    aud: Optional[List[str]]
    username: Optional[str]
    obfuscated_subject: Optional[str]
    ext: Optional[UserAccess]


class InvalidToken(BaseModel):
    """ Token introspection response for an invalid token """
    active: bool = Field(default=False, const=False)
    error: str
