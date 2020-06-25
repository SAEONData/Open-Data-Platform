from typing import List, Optional
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


class AccessInfo(BaseModel):
    user_id: str
    superuser: bool
    access_rights: List[AccessRight]


class AccessToken(BaseModel):
    token_type: TokenType
    active: bool
    client_id: str
    scope: str
    aud: Optional[List[str]]
    sub: str
    iss: str
    iat: int
    exp: int
    ext: Optional[AccessInfo]


class UserProfile(BaseModel):
    user_id: str
    email: EmailStr


class AuthorizationRequest(BaseModel):
    """
    Information provided by a calling API for validating a token in respect of a single request
    that is being made to that API.

    The token itself is an opaque, encrypted string that is associated with a particular user,
    the user's privileges, and a client application. The remaining fields dictate what must be
    true about the info associated with the token in order for the request to be allowed.
    """
    token: str = Field(..., description="The token received by the calling API from a client application.")
    scope: str = Field(..., description="The scope applicable to the request.")
    institution: str = Field(None, description="The institution applicable to the request (if the request relates "
                                               "to an institutional resource).")
    institutional_roles: List[str] = Field([], description="List of roles that the user may have, within the given "
                                                           "institution, in order for the request to be allowed.")
    super_roles: List[str] = Field([], description="List of roles that the user may have, regardless of their "
                                                   "institutional membership, in order for the request to be allowed.")
