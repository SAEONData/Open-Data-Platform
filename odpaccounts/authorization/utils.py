from typing import List

from sqlalchemy.orm import Session

from ..models.privilege import Privilege
from ..models.user import User
from ..models.scope import Scope
from ..authorization.models import AuthorizedUser, Capacity


def create_authorized_user(db_session: Session, user: User, scopes: List[str]) -> AuthorizedUser:
    """
    Create an :class:`AuthorizedUser` instance, which is suitable for attachment to the
    access token for this user. This data will be recoverable from the 'ext' attribute
    when introspecting/validating a token.

    Privileges are filtered to include only those applicable to the requested scopes.
    If the user is a superuser, privileges will be an empty list, since a superuser
    can do anything anyway.

    :param db_session: SQLAlchemy session
    :param user: a User instance
    :param scopes: list of scopes being requested for the token
    :return: AuthorizedUser
    """
    if user.superuser:
        return AuthorizedUser(
            user_id=user.id,
            superuser=True,
            capacities=[],
        )

    privileges = db_session.query(Privilege).filter_by(user_id=user.id) \
        .join(Scope, Privilege.scope_id == Scope.id).filter(Scope.key.in_(scopes)) \
        .all()

    return AuthorizedUser(
        user_id=user.id,
        superuser=False,
        capacities=[Capacity(
            institution_key=privilege.institution.key,
            institution_name=privilege.institution.name,
            role_key=privilege.role.key,
            role_name=privilege.role.name,
            scope_key=privilege.scope.key,
        ) for privilege in privileges],
    )
