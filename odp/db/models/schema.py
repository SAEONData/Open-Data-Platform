from sqlalchemy import Column, String, Enum

from odp.db import Base
from odp.db.models.types import SchemaType


class Schema(Base):
    """Represents a reference to a JSON schema document."""

    __tablename__ = 'schema'

    id = Column(String, unique=True, primary_key=True)
    type = Column(Enum(SchemaType), primary_key=True)
    uri = Column(String, nullable=False)

    def __repr__(self):
        return self._repr('id', 'type', 'uri')
