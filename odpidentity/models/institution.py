from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .user_institution import UserInstitution
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

    # many-to-many institutions-users relationship via association object
    _users = relationship('UserInstitution',
                          back_populates='institution',
                          cascade='all, delete-orphan',
                          passive_deletes=True)
    # enables working with the other side of the relationship transparently
    users = association_proxy('_users', 'user',
                              creator=lambda u: UserInstitution(user=u))
