from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .capability import Capability


class Role(db.Model):
    """
    Model representing a generic role.
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)

    # many-to-many relationship between scope and role represented by capability
    capabilities = relationship('Capability',
                                back_populates='role',
                                cascade='all, delete-orphan',
                                passive_deletes=True)
    # enables working with the other side of the relationship transparently
    scopes = association_proxy('capabilities', 'scope',
                               creator=lambda s: Capability(scope=s))

    def __repr__(self):
        return '<Role %s>' % self.code
