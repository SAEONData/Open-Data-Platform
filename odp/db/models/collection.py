from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base


class Collection(Base):
    """A collection of ODP records."""

    __tablename__ = 'collection'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    doi_key = Column(String)

    provider_id = Column(String, ForeignKey('provider.id', ondelete='CASCADE'), nullable=False)
    provider = relationship('Provider')

    # view of associated projects via many-to-many project_collection relation
    collection_projects = relationship('ProjectCollection', viewonly=True)
    projects = association_proxy('collection_projects', 'project')

    # view of associated flags (one-to-many)
    flags = relationship('CollectionFlag', viewonly=True)

    # view of associated tags (one-to-many)
    tags = relationship('CollectionTag', viewonly=True)

    def __repr__(self):
        return self._repr('id', 'name', 'doi_key', 'provider_id')
