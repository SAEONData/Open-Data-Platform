import os
from typing import List, Tuple

from odp.api.models.auth import AccessTokenData, AccessRight, IDTokenData
from odp.db import session as db_session
from odp.db.models.privilege import Privilege
from odp.db.models.scope import Scope
from odp.db.models.user import User


def get_token_data(user: User, scopes: List[str]) -> Tuple[AccessTokenData, IDTokenData]:
    """
    Return user access and profile information, which may be associated with a user's
    access and id tokens, respectively.

    Privileges are filtered to include only those applicable to the requested scopes.
    If the user is a superuser, access_rights will be an empty list, since a superuser
    can do anything anyway.

    :param user: a User instance
    :param scopes: list of scopes being requested for the token
    :return: tuple(AccessTokenData, IDTokenData)
    """
    id_token_data = IDTokenData(
        user_id=user.id,
        email=user.email,
        role=[],
    )

    if user.superuser:
        access_token_data = AccessTokenData(
            user_id=user.id,
            superuser=True,
            access_rights=[],
        )
    else:
        privileges = db_session.query(Privilege).filter_by(user_id=user.id) \
            .join(Scope, Privilege.scope_id == Scope.id).filter(Scope.key.in_(scopes)) \
            .all()

        access_token_data = AccessTokenData(
            user_id=user.id,
            superuser=False,
            access_rights=[AccessRight(
                institution_key=privilege.institution.key,
                institution_name=privilege.institution.name,
                role_key=privilege.role.key,
                role_name=privilege.role.name,
                scope_key=privilege.scope.key,
            ) for privilege in privileges],
        )

        # see comments in IDTokenData regarding usage of the `role` field
        scope_hits = set()
        for privilege in privileges:
            if privilege.institution.key == os.environ['ADMIN_INSTITUTION']:
                scope_hits |= {privilege.scope.key}
                id_token_data.role += [privilege.role.key]
        if len(scope_hits) > 1:
            id_token_data.role = []

    return access_token_data, id_token_data


def check_access(
        access_token_data: AccessTokenData,
        require_superuser: bool = False,
        require_scope: str = None,
        require_role: str = None,
        require_institution: str = None,
        allow_admin_institution_override: bool = False,
) -> bool:
    """
    Determine whether the access rights associated with a user's access
    token fulfil the parameterised access requirements for a request.

    If require_superuser is True, the remaining parameters are ignored;
    the user must be a superuser in order to carry out the request.

    Otherwise, require_scope, require_role and require_institution
    indicate the corresponding tuple that must be present in the
    access token data, in order for the request to be allowed.

    If allow_admin_institution_override is True, a user with the required
    scope and role within the admin institution will be considered to
    have that capability within all institutions. An example of such a
    usage would be for a curator-type role.

    To ensure that a request is only allowed for members of the admin
    institution with the specified capability, call this function with
    allow_admin_institution_override=True and require_institution=None.
    """
    if require_superuser:
        return access_token_data.superuser

    admin_institution = os.environ['ADMIN_INSTITUTION']

    return any(
        access_right.scope_key == require_scope and
        access_right.role_key == require_role and
        (access_right.institution_key == require_institution or
         (access_right.institution_key == admin_institution and
          allow_admin_institution_override))
        for access_right in access_token_data.access_rights
    )
