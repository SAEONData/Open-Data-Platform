from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.project_collection import ProjectCollection


class Collection(Base):
    """A collection of ODP records."""

    __tablename__ = 'collection'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    doi_key = Column(String)

    provider_id = Column(String, ForeignKey('provider.id', ondelete='CASCADE'), nullable=False)
    provider = relationship('Provider', back_populates='collections')

    # many-to-many relationship between collection and project
    collection_projects = relationship('ProjectCollection', back_populates='collection', cascade='all, delete-orphan', passive_deletes=True)
    projects = association_proxy('collection_projects', 'project', creator=lambda p: ProjectCollection(project=p))

    def __repr__(self):
        return self._repr('id', 'name', 'provider_id')
