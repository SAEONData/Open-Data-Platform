from typing import List
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class TokenType(Enum):
    access = 'access_token'
    refresh = 'refresh_token'


class Capacity(BaseModel):
    institution_key: str
    institution_name: str
    role_key: str
    role_name: str
    scope_key: str


class AuthorizedUser(BaseModel):
    user_id: str
    superuser: bool
    capacities: List[Capacity]


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
    ext: AuthorizedUser


class IDToken(BaseModel):
    sub: str
    email: EmailStr
