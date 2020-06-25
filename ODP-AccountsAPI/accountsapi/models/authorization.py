from typing import List

from pydantic import BaseModel, Field


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
