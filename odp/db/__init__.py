from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from odp.config import config

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
        Session.flush()

    def delete(self):
        Session.delete(self)
        Session.flush()

    def _repr(self, *attrs):
        params = ', '.join(f'{attr}={getattr(self, attr)!r}' for attr in attrs)
        return f'{self.__class__.__name__}({params})'


Base = declarative_base(cls=_Base)
