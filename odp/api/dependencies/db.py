from typing import Generator

from sqlalchemy.orm import Session


def get_db_session() -> Generator[Session, None, None]:
    """
    Database session dependency.
    """
    from odp.db import session
    try:
        yield session
    finally:
        session.remove()
