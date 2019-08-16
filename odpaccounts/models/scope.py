from . import db
from .static_data_mixin import StaticDataMixin


class Scope(StaticDataMixin, db.Model):
    """
    Model representing an OAuth2 / application scope.
    """

    # many-to-many scopes-roles relationship
    roles = db.relationship('Role',
                            secondary='scoped_role',
                            back_populates='scopes',
                            passive_deletes=True)
