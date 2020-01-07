from sqlalchemy.ext.declarative import declarative_base

from ..db import engine

Base = declarative_base()


def create_all():
    Base.metadata.create_all(bind=engine)


def drop_all():
    Base.metadata.drop_all(bind=engine)
