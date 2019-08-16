from . import db

# association table for role-scope relationship
scoped_role = db.Table(
    'scoped_role',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True),
    db.Column('scope_id', db.Integer, db.ForeignKey('scope.id', ondelete='CASCADE'), primary_key=True),
)
