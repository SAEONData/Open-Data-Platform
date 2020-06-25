def db_session():
    """
    Database session dependency.
    :return: SQLAlchemy session
    """
    from odpaccounts.db import session
    from odpaccounts.models.user import User
    from odpaccounts.models.member import Member
    from odpaccounts.models.privilege import Privilege
    from odpaccounts.models.role import Role
    from odpaccounts.models.scope import Scope
    from odpaccounts.models.capability import Capability
    from odpaccounts.models.institution import Institution
    try:
        yield session
    finally:
        session.remove()
