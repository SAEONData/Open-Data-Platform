from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class InstitutionRegistry(Base):
    """
    Model representing an institution registry.
    """
    __tablename__ = 'institution_registry'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)

    institutions = relationship('Institution',
                                back_populates='registry',
                                passive_deletes=True)

    def __repr__(self):
        return '<InstitutionRegistry %s>' % self.code
