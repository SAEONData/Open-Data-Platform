from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from odp.config import config

engine = create_engine(config.ODP.DB.URL, echo=config.ODP.DB.ECHO)

session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


@contextmanager
def transactional_session():
    try:
        yield (s := session())
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()
