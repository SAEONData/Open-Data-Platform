from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from odp.config import config

engine = create_engine(config.ODP.DB.URL, echo=config.ODP.DB.ECHO)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


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
