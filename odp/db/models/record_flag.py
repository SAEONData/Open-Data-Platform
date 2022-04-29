from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, ForeignKeyConstraint, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import AuditCommand, FlagType


class RecordFlag(Base):
    """Flag instance model, representing a flag attached by a user to
    a record.

    Only one instance of a given flag id may be attached to a given record.

    user_id is nullable to allow flags to be set by the system.
    """

    __tablename__ = 'record_flag'

    __table_args__ = (
        ForeignKeyConstraint(
            ('flag_id', 'flag_type'), ('flag.id', 'flag.type'),
            name='record_flag_flag_fkey', ondelete='CASCADE',
        ),
        CheckConstraint(
            f"flag_type = '{FlagType.record}'",
            name='record_flag_flag_type_check',
        ),
    )

    record_id = Column(String, ForeignKey('record.id', ondelete='CASCADE'), primary_key=True)
    flag_id = Column(String, primary_key=True)
    flag_type = Column(Enum(FlagType), primary_key=True)

    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'))
    data = Column(JSONB, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    record = relationship('Record')
    flag = relationship('Flag')
    user = relationship('User')


class RecordFlagAudit(Base):
    """Record flag audit log."""

    __tablename__ = 'record_flag_audit'

    id = Column(Integer, primary_key=True)
    client_id = Column(String, nullable=False)
    user_id = Column(String)
    command = Column(Enum(AuditCommand), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _record_id = Column(String, nullable=False)
    _flag_id = Column(String, nullable=False)
    _user_id = Column(String)
    _data = Column(JSONB)
