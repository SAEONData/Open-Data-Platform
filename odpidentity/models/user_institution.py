from . import db


class UserInstitution(db.Model):
    """
    Model representing a user-institution relation.
    """
    user_id = db.Column(db.String, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    # disallow deleting of an institution if it has any users
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id', ondelete='RESTRICT'), primary_key=True)

    user = db.relationship('User', back_populates='_institutions')
    institution = db.relationship('Institution', back_populates='_users')
