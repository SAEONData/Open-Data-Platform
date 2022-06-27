from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base


class Collection(Base):
    """A collection of ODP records."""

    __tablename__ = 'collection'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    doi_key = Column(String)

    provider_id = Column(String, ForeignKey('provider.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    provider = relationship('Provider')

    # view of associated projects via many-to-many project_collection relation
    collection_projects = relationship('ProjectCollection', viewonly=True)
    projects = association_proxy('collection_projects', 'project')

    # view of associated tags (one-to-many)
    tags = relationship('CollectionTag', viewonly=True)

    # view of associated roles (zero-or-one-to-many)
    roles = relationship('Role', viewonly=True)

    # view of associated clients (zero-or-one-to-many)
    clients = relationship('Client', viewonly=True)

    _repr_ = 'id', 'name', 'doi_key', 'provider_id'
