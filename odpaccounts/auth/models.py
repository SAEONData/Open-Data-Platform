from typing import List
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class TokenType(Enum):
    access = 'access_token'
    refresh = 'refresh_token'


class AccessRight(BaseModel):
    institution_key: str
    institution_name: str
    role_key: str
    role_name: str
    scope_key: str


class AccessRights(BaseModel):
    user_id: str
    superuser: bool
    rights: List[AccessRight]


class AccessToken(BaseModel):
    active: bool = Field(..., const=True)
    token_type: TokenType
    client_id: str
    scope: str
    aud: List[str]
    sub: str
    iss: str
    iat: int
    exp: int
    ext: AccessRights


class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
