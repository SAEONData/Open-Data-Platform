from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import Base
from .capability import Capability


class Scope(Base):
    """
    Model representing an OAuth2 / application scope.
    """
    __tablename__ = 'scope'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    description = Column(String)

    # many-to-many relationship between scope and role represented by capability
    capabilities = relationship('Capability',
                                back_populates='scope',
                                cascade='all, delete-orphan',
                                passive_deletes=True)
    # enables working with the other side of the relationship transparently
    roles = association_proxy('capabilities', 'role',
                              creator=lambda r: Capability(role=r))

    def __repr__(self):
        return '<Scope %s>' % self.key
