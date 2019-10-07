from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .role_scope import RoleScope
from .static_data_mixin import StaticDataMixin


class Scope(StaticDataMixin, db.Model):
    """
    Model representing an OAuth2 / application scope.
    """

    # many-to-many scopes-roles relationship via association object
    scope_roles = relationship('RoleScope',
                               back_populates='scope',
                               cascade='all, delete-orphan',
                               passive_deletes=True)
    # enables working with the other side of the relationship transparently
    roles = association_proxy('scope_roles', 'role',
                              creator=lambda r: RoleScope(role=r))
