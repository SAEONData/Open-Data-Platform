from . import db
from .static_data_mixin import StaticDataMixin


class Institution(StaticDataMixin, db.Model):
    """
    Model representing an institution.
    """

    # allow institutions to be hierarchically related
    parent_id = db.Column(db.Integer, db.ForeignKey('institution.id', ondelete='CASCADE'))
    children = db.relationship('Insitution', passive_deletes=True)

    registry_id = db.Column(db.Integer, db.ForeignKey('institution_registry.id', ondelete='CASCADE'))
    registry = db.relationship('InsitutionRegistry', back_populates='institutions')

    __table_args__ = (
        # a top-level institution must be linked to a registry; a sub-institution must only be linked to its parent
        db.CheckConstraint('(parent_id is null and registry_id is not null) or (parent_id is not null and registry_id is null)'),
    )

    # many-to-many institutions-users relationship
    users = db.relationship('User',
                            secondary='institutional_user',
                            back_populates='institutions',
                            passive_deletes=True)
