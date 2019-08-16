from . import db

# association table for user-institution relationship
institutional_user = db.Table(
    'institutional_user',
    db.Column('user_id', db.String, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    # disallow deleting of an institution if it has any users
    db.Column('institution_id', db.Integer, db.ForeignKey('institution.id', ondelete='RESTRICT'), primary_key=True),
)
