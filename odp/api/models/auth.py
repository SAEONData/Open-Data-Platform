from enum import Enum
from typing import List, Optional, Set, Dict, Literal, Union

from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    ADMIN = 'admin'
    CURATOR = 'curator'
    HARVESTER = 'harvester'
    CONTRIBUTOR = 'contributor'
    MANAGER = 'manager'
    STAFF = 'staff'
    DATASCIENTIST = 'datascientist'

    @staticmethod
    def all():
        return (role for role in Role)


class Scope(str, Enum):
    ADMIN = 'ODP.Admin'
    METADATA = 'ODP.Metadata'
    CATALOGUE = 'ODP.Catalogue'


class TokenUse(str, Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


class ScopeContext(BaseModel):
    projects: Union[Set[str], Literal['*']]
    providers: Union[Set[str], Literal['*']]
    collections: Set[str]


class UserAccess(BaseModel):
    scopes: Dict[str, Union[ScopeContext, Literal['*']]]


class UserInfo(BaseModel):
    sub: str
    email: EmailStr
    email_verified: bool
    name: Optional[str]
    picture: Optional[str]
    roles: List[str]


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
