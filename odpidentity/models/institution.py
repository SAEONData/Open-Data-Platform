from . import db
from .static_data_mixin import StaticDataMixin


class Institution(StaticDataMixin, db.Model):
    """
    Model representing an institution.
    """
    id = db.Column(db.Integer, primary_key=True)

    # institutions can be hierarchically related
    parent_id = db.Column(db.Integer)
    parent = db.relationship('Institution',
                             backref='children',
                             remote_side=[id],
                             primaryjoin=parent_id == id)

    registry_id = db.Column(db.Integer, db.ForeignKey('institution_registry.id', ondelete='CASCADE'), nullable=False)
    registry = db.relationship('InstitutionRegistry', back_populates='institutions')

    __table_args__ = (
        # ensure that hierarchically-related institutions are in the same registry
        db.UniqueConstraint('id', 'registry_id'),
        db.ForeignKeyConstraint(
            ['parent_id', 'registry_id'],
            ['institution.id', 'institution.registry_id'],
            ondelete='CASCADE',
        ),
    )

    # many-to-many institutions-users relationship
    users = db.relationship('User',
                            secondary='institutional_user',
                            back_populates='institutions',
                            passive_deletes=True)
