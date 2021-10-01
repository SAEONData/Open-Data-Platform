from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.project_collection import ProjectCollection


class Collection(Base):
    """A collection of ODP records."""

    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)

    provider_id = Column(Integer, ForeignKey('provider.id', ondelete='CASCADE'), nullable=False)
    provider = relationship('Provider', back_populates='collections')

    # many-to-many relationship between collection and project
    collection_projects = relationship('ProjectCollection', back_populates='collection', cascade='all, delete-orphan', passive_deletes=True)
    projects = association_proxy('collection_projects', 'project', creator=lambda p: ProjectCollection(project=p))

    def __repr__(self):
        return self._repr('id', 'key', 'name', 'provider')
