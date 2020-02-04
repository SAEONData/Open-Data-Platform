from typing import List
from enum import Enum

from pydantic import BaseModel, EmailStr


class TokenType(Enum):
    access = 'access_token'
    refresh = 'refresh_token'


class AccessRight(BaseModel):
    institution_key: str
    institution_name: str
    role_key: str
    role_name: str
    scope_key: str


class AccessInfo(BaseModel):
    user_id: str
    superuser: bool
    access_rights: List[AccessRight]


class AccessToken(BaseModel):
    token_type: TokenType
    active: bool
    client_id: str
    scope: str
    aud: List[str]
    sub: str
    iss: str
    iat: int
    exp: int
    ext: AccessInfo


class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
