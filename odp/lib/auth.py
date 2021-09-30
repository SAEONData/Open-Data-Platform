from typing import Union, Set, Literal, Dict, Optional, List

from pydantic import BaseModel, EmailStr

from odp.db import Session
from odp.db.models import User, Client
from odp.lib import exceptions as x


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


def get_user_access(user_id: str, client_id: str) -> UserAccess:
    """Return user access information, which may be linked with a user's access
    token for a given client application.

    The resultant UserAccess object represents the effective set of permissions
    for the given user working within the given client. It consists of a dictionary
    of scope ids (OAuth2 scope identifiers), where the value for each id is either:

    - '*' if the scope is applicable across all relevant platform entities; or
    - a ScopeContext object indicating the projects and/or providers to which the
      scope's usage is limited; in this case 'projects' or 'providers' may also
      take the value '*' if unrestricted.
    """
    user = Session.get(User, user_id)
    if not user:
        raise x.ODPUserNotFound

    client = Session.get(Client, client_id)
    if not client:
        raise x.ODPClientNotFound

    unpinned_scopes = set()
    for role in user.roles:
        if role.client_id not in (None, client_id):
            continue
        if not role.project and not role.provider:
            unpinned_scopes |= {
                scope.id for scope in role.scopes
                if scope in client.scopes
            }

    pinned_scopes = {}
    for role in user.roles:
        if role.client_id not in (None, client_id):
            continue
        if role.project or role.provider:
            for scope in role.scopes:
                if scope.id in unpinned_scopes:
                    continue
                if scope not in client.scopes:
                    continue
                pinned_scopes.setdefault(scope.id, dict(
                    projects=set(), providers=set()
                ))
                if role.project:
                    pinned_scopes[scope.id]['projects'] |= {role.project.key}
                if role.provider:
                    pinned_scopes[scope.id]['providers'] |= {role.provider.key}

    return UserAccess(
        scopes={scope: '*' for scope in unpinned_scopes} | {scope: ScopeContext(
            projects=projects if (projects := pinned_scopes[scope]['projects']) else '*',
            providers=providers if (providers := pinned_scopes[scope]['providers']) else '*',
        ) for scope in pinned_scopes}
    )


def get_user_info(user_id: str, client_id: str) -> UserInfo:
    """Return user profile info, which may be linked with a user's
    ID token for a given client application.

    TODO: we should limit the returned info based on the claims
     allowed for the client
    """
    user = Session.get(User, user_id)
    if not user:
        raise x.ODPUserNotFound

    return UserInfo(
        sub=user_id,
        email=user.email,
        email_verified=user.verified,
        name=user.name,
        picture=user.picture,
        roles=[
            role.id for role in user.roles
            if role.client_id in (None, client_id)
        ],
    )
