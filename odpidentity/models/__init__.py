import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    os.getenv('DATABASE_URL'),
    echo=os.getenv('DATABASE_ECHO', '').lower() == 'true',
)

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


def init_app(app):
    # ensure that the db session is closed and disposed after each request
    @app.teardown_appcontext
    def discard_session(exc):
        db_session.remove()


def init_db(drop_all):
    if drop_all:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
