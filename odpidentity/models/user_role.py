from . import db


class UserRole(db.Model):
    """
    Model representing a user-institution-role-scope relation.
    """
    user_id = db.Column(db.String, primary_key=True)
    institution_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, primary_key=True)
    scope_id = db.Column(db.Integer, primary_key=True)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['user_id', 'institution_id'],
            ['user_institution.user_id', 'user_institution.institution_id'],
            name='user_role_user_id_institution_id_fkey',
            ondelete='CASCADE',
        ),
        db.ForeignKeyConstraint(
            ['role_id', 'scope_id'],
            ['role_scope.role_id', 'role_scope.scope_id'],
            name='user_role_role_id_scope_id_fkey',
            ondelete='CASCADE',
        ),
    )

    user = db.relationship('User', primaryjoin='UserRole.user_id == User.id', foreign_keys=user_id)
    institution = db.relationship('Institution', primaryjoin='UserRole.institution_id == Institution.id', foreign_keys=institution_id)
    role = db.relationship('Role', primaryjoin='UserRole.role_id == Role.id', foreign_keys=role_id)
    scope = db.relationship('Scope', primaryjoin='UserRole.scope_id == Scope.id', foreign_keys=scope_id)
