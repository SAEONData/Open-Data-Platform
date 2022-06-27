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
    name = Column(String, nullable=False)

    # view of associated collections (one-to-many)
    collections = relationship('Collection', viewonly=True)

    _repr_ = 'id', 'name'
