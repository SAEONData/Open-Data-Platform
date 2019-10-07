from . import db


class RoleScope(db.Model):
    """
    Model representing a role-scope relation.
    """
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    scope_id = db.Column(db.Integer, db.ForeignKey('scope.id', ondelete='CASCADE'), primary_key=True)

    role = db.relationship('Role', back_populates='role_scopes')
    scope = db.relationship('Scope', back_populates='scope_roles')
