from sqlalchemy import Column, String

from odp.db import Base


class MetadataSchema(Base):
    """A JSON schema for validating ODP records."""

    __tablename__ = 'metadata_schema'

    id = Column(String, primary_key=True)
    schema_uri = Column(String, nullable=False)

    def __repr__(self):
        return self._repr('id', 'schema_uri')
