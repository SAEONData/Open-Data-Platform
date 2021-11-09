from dataclasses import dataclass
from typing import Union, Literal, Dict, Optional, List

from odp.db import Session
from odp.db.models import User, Client
from odp.lib import exceptions as x


@dataclass
class Authorization:
    """An Authorization object represents the effective set of permissions
    for a user or a client. It consists of a dictionary of scope ids (OAuth2
    scope identifiers), where the value for each id is either:

    - '*' if the scope is applicable across all relevant platform entities; or
    - a set of provider ids to which the scope's usage is limited (implemented
      as a list for JSON serialization)
    """
    scopes: Dict[str, Union[Literal['*'], List[str]]]


@dataclass
class UserInfo:
    sub: str
    email: str
    email_verified: bool
    name: Optional[str]
    picture: Optional[str]
    roles: List[str]


def get_client_auth(client_id: str) -> Authorization:
    """Return client authorization info."""
    client = Session.get(Client, client_id)
    if not client:
        raise x.ODPClientNotFound

    return Authorization(
        scopes={scope.id: '*' if not client.provider else [client.provider_id]
                for scope in client.scopes}
    )


def get_user_auth(user_id: str, client_id: str) -> Authorization:
    """Return user authorization info, which may be linked with
    a user's access token for a given client application."""
    user = Session.get(User, user_id)
    if not user:
        raise x.ODPUserNotFound

    client = Session.get(Client, client_id)
    if not client:
        raise x.ODPClientNotFound

    platform_scopes = set()
    if not client.provider:
        for role in user.roles:
            if not role.provider:
                platform_scopes |= {
                    scope.id for scope in role.scopes
                    if scope in client.scopes
                }

    provider_scopes = {}
    for role in user.roles:
        if role.provider or client.provider:
            if role.provider and client.provider and role.provider_id != client.provider_id:
                continue
            for scope in role.scopes:
                if scope.id in platform_scopes:
                    continue
                if scope not in client.scopes:
                    continue
                provider_scopes.setdefault(scope.id, set())
                provider_scopes[scope.id] |= {role.provider_id if role.provider else client.provider_id}

    provider_scopes = {
        scope: list(providers)
        for scope, providers in provider_scopes.items()
    }

    return Authorization(
        scopes={scope: '*' for scope in platform_scopes} | provider_scopes
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

    client = Session.get(Client, client_id)
    if not client:
        raise x.ODPClientNotFound

    return UserInfo(
        sub=user_id,
        email=user.email,
        email_verified=user.verified,
        name=user.name,
        picture=user.picture,
        roles=[
            role.id for role in user.roles
            if not role.provider or not client.provider or role.provider_id == client.provider_id
        ],
    )
