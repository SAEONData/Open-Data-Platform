from sqlalchemy import Column, String, Integer

from odp.db import Base


class DigitalObjectSchema(Base):
    """Model representing a metadata schema for digital objects."""

    __tablename__ = 'digitalobject_schema'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    schema_uri = Column(String, nullable=False)

    def __repr__(self):
        return self._repr('id', 'key', 'schema_uri')
