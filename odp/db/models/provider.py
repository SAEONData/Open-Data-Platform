from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from odp.db import Base


class Provider(Base):
    """Model representing an originating party / owner of a digital object.

    Provider-specific roles permit scope access to only the specified
    provider's collections.
    """

    __tablename__ = 'provider'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)

    # one-to-many relationship with role
    roles = relationship('Role', back_populates='provider', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return self._repr('id', 'key', 'name')
