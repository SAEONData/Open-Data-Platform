from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from odp.db import Base


class Tag(Base):
    """A tag definition."""

    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    public = Column(Boolean, nullable=False)
    schema_uri = Column(String, nullable=False)

    scope_id = Column(String, ForeignKey('scope.id', ondelete='RESTRICT'), nullable=False)
    scope = relationship('Scope')

    def __repr__(self):
        return self._repr('id', 'key', 'public', 'schema_uri', 'scope')
