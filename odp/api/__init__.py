def db_session():
    """
    Database session dependency.
    :return: SQLAlchemy session
    """
    from odp.db import session
    try:
        yield session
    finally:
        session.remove()
