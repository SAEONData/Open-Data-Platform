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
            if privilege.institution.key == os.getenv('ADMIN_INSTITUTION'):
                scope_hits |= {privilege.scope.key}
                id_token_data.role += [privilege.role.key]
        if len(scope_hits) > 1:
            id_token_data.role = []

    return access_token_data, id_token_data
