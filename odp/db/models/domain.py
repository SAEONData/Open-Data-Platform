from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from odp.db import Base


class Domain(Base):
    """
    Model representing a domain owned by an institution.
    """
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    institution_id = Column(Integer, ForeignKey('institution.id', ondelete='CASCADE'), nullable=False)

    institution = relationship('Institution', back_populates='domains')
