from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, Integer, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import AuditCommand


class CollectionFlag(Base):
    """Flag instance model, representing a flag attached by a user to
    a collection.

    Only one flag of a given type may be attached to a collection.

    user_id is nullable to allow flags to be set by the system.
    """

    __tablename__ = 'collection_flag'

    collection_id = Column(String, ForeignKey('collection.id', ondelete='CASCADE'), primary_key=True)
    flag_id = Column(String, ForeignKey('flag.id', ondelete='CASCADE'), primary_key=True)

    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'))
    data = Column(JSONB, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    collection = relationship('Collection')
    flag = relationship('Flag')
    user = relationship('User')


class CollectionFlagAudit(Base):
    """Collection flag audit log."""

    __tablename__ = 'collection_flag_audit'

    id = Column(Integer, primary_key=True)
    client_id = Column(String, nullable=False)
    user_id = Column(String)
    command = Column(Enum(AuditCommand), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _collection_id = Column(String, nullable=False)
    _flag_id = Column(String, nullable=False)
    _user_id = Column(String)
    _data = Column(JSONB)
