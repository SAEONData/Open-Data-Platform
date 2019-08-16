from hydra_client import HydraTokenMixin

from . import db


class HydraToken(HydraTokenMixin, db.Model):
    """
    Represents the OAuth token for a user logged in locally to the identity service.
    """
