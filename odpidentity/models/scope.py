from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .capability import Capability


class Scope(db.Model):
    """
    Model representing an OAuth2 / application scope.
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)

    # many-to-many relationship between scope and role represented by capability
    capabilities = relationship('Capability',
                                back_populates='scope',
                                cascade='all, delete-orphan',
                                passive_deletes=True)
    # enables working with the other side of the relationship transparently
    roles = association_proxy('capabilities', 'role',
                              creator=lambda r: Capability(role=r))

    def __repr__(self):
        return '<Scope %s>' % self.code
