import warnings

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

Session = scoped_session(sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
))


class _Base:
    def save(self):
        Session.add(self)
        self._flush()

    def delete(self):
        Session.delete(self)
        self._flush()

    @staticmethod
    def _flush():
        try:
            Session.flush()
        except Exception:
            Session.rollback()
            raise

    def _repr(self, *attrs):
        params = ', '.join(f'{attr}={getattr(self, attr)!r}' for attr in attrs)
        return f'{self.__class__.__name__}({params})'


Base = declarative_base(cls=_Base)
