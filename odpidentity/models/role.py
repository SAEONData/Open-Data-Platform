from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .static_data_mixin import StaticDataMixin
from .role_scope import RoleScope


class Role(StaticDataMixin, db.Model):
    """
    Model representing a generic role.
    """
    is_admin = db.Column(db.Boolean(), nullable=False)

    # many-to-many scopes-roles relationship via association object
    _scopes = relationship('RoleScope',
                           back_populates='role',
                           cascade='all, delete-orphan',
                           passive_deletes=True)
    # enables working with the other side of the relationship transparently
    scopes = association_proxy('_scopes', 'scope',
                               creator=lambda s: RoleScope(scope=s))
