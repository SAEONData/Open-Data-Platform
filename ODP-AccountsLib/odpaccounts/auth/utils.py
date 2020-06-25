from typing import List

from ..db import session as db_session
from ..models.privilege import Privilege
from ..models.user import User
from ..models.scope import Scope
from ..auth.models import AccessInfo, AccessRight, UserProfile


def get_access_info(user: User, scopes: List[str]) -> AccessInfo:
    """
    Create an :class:`AccessInfo` instance, which is suitable for attachment to the
    access token for this user. This data will be recoverable from the 'ext' attribute
    when introspecting/validating a token.

    Privileges are filtered to include only those applicable to the requested scopes.
    If the user is a superuser, access_rights will be an empty list, since a superuser
    can do anything anyway.

    :param user: a User instance
    :param scopes: list of scopes being requested for the token
    :return: AccessInfo
    """
    if user.superuser:
        return AccessInfo(
            user_id=user.id,
            superuser=True,
            access_rights=[],
        )

    privileges = db_session.query(Privilege).filter_by(user_id=user.id) \
        .join(Scope, Privilege.scope_id == Scope.id).filter(Scope.key.in_(scopes)) \
        .all()

    return AccessInfo(
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


def get_user_profile(user: User) -> UserProfile:
    """
    Create a :class:`UserProfile` instance, which is suitable for generating the ID token
    for this user.

    :param user: a User instance
    :return: UserProfile
    """
    return UserProfile(
        user_id=user.id,
        email=user.email,
    )
