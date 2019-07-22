from . import db

assigned_role = db.Table(
    'assigned_role',
    db.Column('user_id', db.String, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete='RESTRICT'), primary_key=True),
    db.Column('institution_id', db.Integer, db.ForeignKey('institution.id', ondelete='RESTRICT'), primary_key=True),
)
