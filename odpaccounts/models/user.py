import uuid

from flask_login import UserMixin

from . import db


class User(UserMixin, db.Model):
    """
    Model representing a user account.
    """
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean(), nullable=False)
    confirmed_at = db.Column(db.DateTime())

    # many-to-many institutions-users relationship
    institutions = db.relationship('Institution',
                                   secondary='institutional_user',
                                   back_populates='users',
                                   passive_deletes=True)

    def __repr__(self):
        return '<User %r>' % self.email
