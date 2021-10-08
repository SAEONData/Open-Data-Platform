from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from odp.db import Base


class Provider(Base):
    """A data provider.

    This model represents the person, group or organization considered
    to be the originating party of a digital object identified by an
    ODP record.
    """

    __tablename__ = 'provider'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # one-to-many relationship with collection
    collections = relationship('Collection', back_populates='provider', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return self._repr('id', 'name')
