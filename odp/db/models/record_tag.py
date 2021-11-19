from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, Integer, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import AuditCommand


class RecordTag(Base):
    """Tag instance model, representing a tag attached by a user to
    a record.

    The 3-way primary key allows multiple tags of the same type to
    be attached to a given object, but only one such tag per user.
    """

    __tablename__ = 'record_tag'

    record_id = Column(String, ForeignKey('record.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(String, ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)

    data = Column(JSONB, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    record = relationship('Record')
    tag = relationship('Tag')
    user = relationship('User')


class RecordTagAudit(Base):
    """Record tag audit log."""

    __tablename__ = 'record_tag_audit'

    id = Column(Integer, primary_key=True)
    client_id = Column(String, nullable=False)
    user_id = Column(String)
    command = Column(Enum(AuditCommand), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _record_id = Column(String, nullable=False)
    _tag_id = Column(String, nullable=False)
    _user_id = Column(String, nullable=False)
    _data = Column(JSONB)
