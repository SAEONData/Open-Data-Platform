import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.client_scope import ClientScope


class Client(Base):
    """Model representing a client application.

    If a client is linked with a project, then any assigned scopes
    grant access only to resources linked with that project.
    """

    __tablename__ = 'client'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)

    project_id = Column(Integer, ForeignKey('project.id', ondelete='CASCADE'))
    project = relationship('Project', back_populates='clients')

    # many-to-many relationship between client and scope
    client_scopes = relationship('ClientScope', back_populates='client', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('client_scopes', 'scope', creator=lambda s: ClientScope(scope=s))

    def __repr__(self):
        return self._repr('id', 'name', 'project')
