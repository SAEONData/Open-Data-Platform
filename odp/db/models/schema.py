from sqlalchemy import Column, Enum, String, TIMESTAMP

from odp.db import Base
from odp.db.models.types import SchemaType


class Schema(Base):
    """Represents a reference to a JSON schema document."""

    __tablename__ = 'schema'

    id = Column(String, unique=True, primary_key=True)
    type = Column(Enum(SchemaType), primary_key=True)
    uri = Column(String, nullable=False)
    md5 = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _repr_ = 'id', 'type', 'uri'
