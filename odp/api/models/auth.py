from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    ADMIN = 'admin'
    CURATOR = 'curator'
    HARVESTER = 'harvester'
    CONTRIBUTOR = 'contributor'
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


class AccessRight(BaseModel):
    institution_key: str
    institution_name: str
    role_key: str
    role_name: str
    scope_key: str


class AccessTokenData(BaseModel):
    user_id: str
    email: EmailStr
    superuser: bool
    access_rights: List[AccessRight]


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
    ext: Optional[AccessTokenData]


class InvalidToken(BaseModel):
    """ Token introspection response for an invalid token """
    active: bool = Field(default=False, const=False)
    error: str


class IDTokenData(BaseModel):
    sub: str
    email: EmailStr
    email_verified: bool
    family_name: Optional[str]
    given_name: Optional[str]
    picture: Optional[str]

    # The `role` field is used strictly for the special case of indicating a user's
    # role(s) within the admin institution, for the requested scope.
    # If the user is not a member of the admin institution, or multiple applicable
    # capabilities were found (unlikely: an access token will typically be issued
    # for one application scope) then `role` will be left empty.
    role: List[str]
