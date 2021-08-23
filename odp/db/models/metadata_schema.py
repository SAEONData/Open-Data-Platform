from sqlalchemy import Column, String, Integer

from odp.db import Base


class MetadataSchema(Base):
    """Model representing a JSON schema for digital object metadata."""

    __tablename__ = 'metadata_schema'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    schema_uri = Column(String, nullable=False)

    def __repr__(self):
        return self._repr('id', 'key', 'schema_uri')
