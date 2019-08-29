from . import db

# association table for the user-institution-role-scope relationship;
# for a given user affiliated to a given institution, this table indicates the role(s) assigned to
# that user within the context of that institution, and the scope(s) to which the role(s) apply
user_role = db.Table(
    'user_role',
    db.Column('user_id', db.String, primary_key=True),
    db.Column('institution_id', db.Integer, primary_key=True),
    db.Column('role_id', db.Integer, primary_key=True),
    db.Column('scope_id', db.Integer, primary_key=True),

    db.ForeignKeyConstraint(
        ['user_id', 'institution_id'],
        ['institutional_user.user_id', 'institutional_user.institution_id'],
        name='user_role_fkey_user_institution',
        ondelete='CASCADE',
    ),
    db.ForeignKeyConstraint(
        ['role_id', 'scope_id'],
        ['scoped_role.role_id', 'scoped_role.scope_id'],
        name='user_role_fkey_role_scope',
        ondelete='CASCADE',
    ),
)
