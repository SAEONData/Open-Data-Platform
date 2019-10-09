from . import db


class Actor(db.Model):
    """
    Model of a member-capability relationship (institution-user-scope-role),
    representing an actor on the platform. Access tokens are issued to actors.
    """
    id = db.Column(db.Integer, primary_key=True)

    member_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete='CASCADE'))
    capability_id = db.Column(db.Integer, db.ForeignKey('capability.id', ondelete='CASCADE'))

    member = db.relationship('Member', back_populates='actors')
    capability = db.relationship('Capability', back_populates='actors')

    __table_args__ = (
        db.UniqueConstraint('member_id', 'capability_id'),
    )
