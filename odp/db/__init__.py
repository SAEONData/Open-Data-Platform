import warnings
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import RemovedIn20Warning
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from odp.config import config

warnings.filterwarnings('default', category=RemovedIn20Warning)

engine = create_engine(
    config.ODP.DB.URL,
    echo=config.ODP.DB.ECHO,
    future=True,
)

session = scoped_session(sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
))


@contextmanager
def transaction():
    """Provide a transactional scope around a series of operations."""
    try:
        yield
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class _Base:
    query = session.query_property()

    def save(self):
        session.add(self)
        self._flush()

    def delete(self):
        session.delete(self)
        self._flush()

    @staticmethod
    def _flush():
        try:
            session.flush()
        except Exception:
            session.rollback()
            raise


Base = declarative_base(cls=_Base)
