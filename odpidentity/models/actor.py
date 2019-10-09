from . import db


class Actor(db.Model):
    """
    Model of a member-capability relationship (institution-user-scope-role),
    representing an actor on the platform. Access tokens are issued to actors.
    """
    institution_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, primary_key=True)
    scope_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, primary_key=True)

    member = db.relationship('Member', back_populates='actors')
    capability = db.relationship('Capability', back_populates='actors')

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['institution_id', 'user_id'],
            ['member.institution_id', 'member.user_id'],
            name='actor_member_fkey',
            ondelete='CASCADE',
        ),
        db.ForeignKeyConstraint(
            ['scope_id', 'role_id'],
            ['capability.scope_id', 'capability.role_id'],
            name='actor_capability_fkey',
            ondelete='CASCADE',
        ),
    )
