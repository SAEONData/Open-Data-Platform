from sqlalchemy import Column, String

from odp.db import Base


class Catalog(Base):
    """Represents a public catalog providing access to published
    digital object records."""

    __tablename__ = 'catalog'

    id = Column(String, primary_key=True)

    _repr_ = 'id',
