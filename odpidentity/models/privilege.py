from . import db


class Privilege(db.Model):
    """
    Model of a member-capability relationship (institution-user-scope-role),
    representing the privilege assigned to a member to use a particular capability.
    """
    institution_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, primary_key=True)
    scope_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, primary_key=True)

    member = db.relationship('Member', back_populates='privileges')
    capability = db.relationship('Capability', back_populates='privileges')

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['institution_id', 'user_id'],
            ['member.institution_id', 'member.user_id'],
            name='privilege_member_fkey',
            ondelete='CASCADE',
        ),
        db.ForeignKeyConstraint(
            ['scope_id', 'role_id'],
            ['capability.scope_id', 'capability.role_id'],
            name='privilege_capability_fkey',
            ondelete='CASCADE',
        ),
    )
