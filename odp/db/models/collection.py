from sqlalchemy import Column, Enum, ForeignKey, Identity, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import AuditCommand


class Collection(Base):
    """A collection of ODP records."""

    __tablename__ = 'collection'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    doi_key = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    provider_id = Column(String, ForeignKey('provider.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    provider = relationship('Provider')

    # view of associated tags (one-to-many)
    tags = relationship('CollectionTag', viewonly=True)

    # view of associated roles (zero-or-one-to-many)
    roles = relationship('Role', viewonly=True)

    # view of associated clients (zero-or-one-to-many)
    clients = relationship('Client', viewonly=True)

    _repr_ = 'id', 'name', 'doi_key', 'provider_id'


class CollectionAudit(Base):
    """Collection audit log."""

    __tablename__ = 'collection_audit'

    id = Column(Integer, Identity(), primary_key=True)
    client_id = Column(String, nullable=False)
    user_id = Column(String)
    command = Column(Enum(AuditCommand), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _id = Column(String, nullable=False)
    _name = Column(String, nullable=False)
    _doi_key = Column(String)
    _provider_id = Column(String, nullable=False)
