from typing import Tuple, Optional

from odp.api.models.auth import (
    UserAccess,
    UserInfo,
    ScopeContext,
    Role as RoleEnum,
    Scope as ScopeEnum,
)
from odp.config import config
from odp.db import session
from odp.db.models import Role, User, Client


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
    user = session.get(User, user_id)
    client = session.get(Client, client_id)

    unpinned_scopes = set()
    for role in user.roles:
        if role.client_id not in (None, client_id):
            continue
        if not role.project_id and not role.provider_id:
            unpinned_scopes |= {
                scope.key for scope in role.scopes
                if scope in client.scopes
            }

    pinned_scopes = {}
    for role in user.roles:
        if role.client_id not in (None, client_id):
            continue
        if role.project_id or role.provider_id:
            for scope in role.scopes:
                if scope.key in unpinned_scopes:
                    continue
                if scope not in client.scopes:
                    continue
                pinned_scopes.setdefault(scope.key, dict(
                    projects=set(), providers=set(), collections=set()
                ))
                if role.project_id:
                    pinned_scopes[scope.key]['projects'] |= role.project.key
                    pinned_scopes[scope.key]['collections'] |= {
                        collection.key for collection in role.project.collections
                    }
                if role.provider_id:
                    pinned_scopes[scope.key]['providers'] |= role.provider.key
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
    user = session.get(User, user_id)
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


def check_access(
        access_token_data: AccessTokenData,
        require_institution: Optional[str],
        require_scope: ScopeEnum,
        require_role: Tuple[RoleEnum, ...],
) -> bool:
    """
    Determine whether the access rights associated with a user's access
    token fulfil the parameterised access requirements for a request.

    require_institution, require_scope and require_role indicate the
    corresponding tuple that must be present in the access token data,
    in order for the request to be allowed. Any of the require_role
    values may match. If require_institution is None, only scope and
    role need match.

    A user with an admin-type role (e.g. 'admin' or 'curator') within
    the admin institution will be considered to have the associated
    capabilities across all institutions.
    """

    def is_admin_role(role_key):
        return session.query(Role.admin).filter_by(key=role_key).scalar()

    if not require_scope or not require_role:
        raise ValueError("require_scope and require_role are mandatory")

    if access_token_data.superuser:
        return True

    admin_institution = config.ODP.ADMIN.INSTITUTION

    return any(
        ar.scope_key == require_scope and
        ar.role_key in require_role and
        (require_institution is None or
         ar.institution_key == require_institution or
         (ar.institution_key == admin_institution and is_admin_role(ar.role_key)))
        for ar in access_token_data.access_rights
    )
