from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, ForeignKeyConstraint, Identity, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import AuditCommand, SchemaType, ScopeType


class Vocabulary(Base):
    """A vocabulary is a collection of terms, each of which is
    structured according to the schema for the vocabulary."""

    __tablename__ = 'vocabulary'

    __table_args__ = (
        ForeignKeyConstraint(
            ('schema_id', 'schema_type'), ('schema.id', 'schema.type'),
            name='vocabulary_schema_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"schema_type = '{SchemaType.vocabulary}'",
            name='vocabulary_schema_type_check',
        ),
        ForeignKeyConstraint(
            ('scope_id', 'scope_type'), ('scope.id', 'scope.type'),
            name='vocabulary_scope_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"scope_type = '{ScopeType.odp}'",
            name='vocabulary_scope_type_check',
        ),
    )

    id = Column(String, unique=True, primary_key=True)

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    scope_id = Column(String, nullable=False)
    scope_type = Column(Enum(ScopeType), nullable=False)
    scope = relationship('Scope')

    # view of associated terms (one-to-many)
    terms = relationship('VocabularyTerm', viewonly=True)

    _repr_ = 'id', 'schema_id', 'scope_id'


class VocabularyTerm(Base):
    """A term in a vocabulary."""

    __tablename__ = 'vocabulary_term'

    vocabulary_id = Column(String, ForeignKey('vocabulary.id', ondelete='CASCADE'), primary_key=True)
    term_id = Column(String, primary_key=True)
    data = Column(JSONB, nullable=False)

    vocabulary = relationship('Vocabulary')

    _repr_ = 'vocabulary_id', 'term_id'


class VocabularyTermAudit(Base):
    """Vocabulary term audit log."""

    __tablename__ = 'vocabulary_term_audit'

    id = Column(Integer, Identity(), primary_key=True)
    client_id = Column(String, nullable=False)
    user_id = Column(String)
    command = Column(Enum(AuditCommand), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _vocabulary_id = Column(String, nullable=False)
    _term_id = Column(String, nullable=False)
    _data = Column(JSONB, nullable=False)
