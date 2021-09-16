from odp.api.models.auth import UserAccess, UserInfo, ScopeContext
from odp.db import Session
from odp.db.models import User, Client


def get_user_access(user_id: str, client_id: str) -> UserAccess:
    """Return user access information, which may be linked with a user's access
    token for a given client application.

    The resultant UserAccess object represents the effective set of permissions
    for the given user working within the given client. It consists of a dictionary
    of scope keys (which are OAuth2 scope identifiers), where the value of each
    key is either:

    - '*' if the scope is applicable across all relevant platform entities; or
    - a ScopeContext object indicating the projects, providers and collections to
      which the scope's usage is limited; in this case 'projects' or 'providers'
      may also take the value '*' if unrestricted.
    """
    user = Session.get(User, user_id)
    client = Session.get(Client, client_id)

    unpinned_scopes = set()
    for role in user.roles:
        if role.client_id not in (None, client_id):
            continue
        if not role.project and not role.provider:
            unpinned_scopes |= {
                scope.key for scope in role.scopes
                if scope in client.scopes
            }

    pinned_scopes = {}
    for role in user.roles:
        if role.client_id not in (None, client_id):
            continue
        if role.project or role.provider:
            for scope in role.scopes:
                if scope.key in unpinned_scopes:
                    continue
                if scope not in client.scopes:
                    continue
                pinned_scopes.setdefault(scope.key, dict(
                    projects=set(), providers=set(), collections=set()
                ))
                if role.project:
                    pinned_scopes[scope.key]['projects'] |= {role.project.key}
                    pinned_scopes[scope.key]['collections'] |= {
                        collection.key for collection in role.project.collections
                    }
                if role.provider:
                    pinned_scopes[scope.key]['providers'] |= {role.provider.key}
                    pinned_scopes[scope.key]['collections'] |= {
                        collection.key for collection in role.provider.collections
                    }

    return UserAccess(
        scopes={scope: '*' for scope in unpinned_scopes} | {scope: ScopeContext(
            projects=projects if (projects := pinned_scopes[scope]['projects']) else '*',
            providers=providers if (providers := pinned_scopes[scope]['providers']) else '*',
            collections=pinned_scopes[scope]['collections'],
        ) for scope in pinned_scopes}
    )


def get_user_info(user_id: str, client_id: str) -> UserInfo:
    """Return user profile info, which may be linked with a user's
    ID token for a given client application.

    TODO: we should limit the returned info based on the claims
     allowed for the client
    """
    user = Session.get(User, user_id)
    return UserInfo(
        sub=user_id,
        email=user.email,
        email_verified=user.verified,
        name=user.name,
        picture=user.picture,
        roles=[
            role.key for role in user.roles
            if role.client_id in (None, client_id)
        ],
    )
