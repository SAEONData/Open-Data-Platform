def db_session():
    """
    Database session dependency.
    :return: SQLAlchemy session
    """
    from odp.db import session
    from odp.db.models.user import User
    from odp.db.models.member import Member
    from odp.db.models.privilege import Privilege
    from odp.db.models.role import Role
    from odp.db.models.scope import Scope
    from odp.db.models.capability import Capability
    from odp.db.models.institution import Institution
    try:
        yield session
    finally:
        session.remove()
