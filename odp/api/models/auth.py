from enum import Enum
from typing import List, Optional, Set, Dict, Literal, Union

from pydantic import BaseModel, EmailStr, Field


class SystemScope(str, Enum):
    CATALOGUE_MANAGE = 'ODP.catalogue:manage'
    CATALOGUE_VIEW = 'ODP.catalogue:view'
    CLIENT_MANAGE = 'ODP.client:manage'
    CLIENT_VIEW = 'ODP.client:view'
    COLLECTION_MANAGE = 'ODP.collection:manage'
    COLLECTION_VIEW = 'ODP.collection:view'
    DIGITALOBJECT_MANAGE = 'ODP.digitalobject:manage'
    DIGITALOBJECT_VIEW = 'ODP.digitalobject:view'
    PROJECT_MANAGE = 'ODP.project:manage'
    PROJECT_VIEW = 'ODP.project:view'
    PROVIDER_MANAGE = 'ODP.provider:manage'
    PROVIDER_VIEW = 'ODP.provider:view'
    ROLE_MANAGE = 'ODP.role:manage'
    ROLE_VIEW = 'ODP.role:view'
    SCOPE_MANAGE = 'ODP.scope:manage'
    SCOPE_VIEW = 'ODP.scope:view'
    USER_MANAGE = 'ODP.user:manage'
    USER_VIEW = 'ODP.user:view'


class TokenUse(str, Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


class ScopeContext(BaseModel):
    projects: Union[Set[str], Literal['*']]
    providers: Union[Set[str], Literal['*']]


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
