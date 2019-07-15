from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from . import db


class HydraToken(OAuthConsumerMixin, db.Model):
    """
    Represents the OAuth token for a user logged in locally to the accounts service.
    """
    __tablename__ = 'hydra_token'
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    # todo create index on provider column
