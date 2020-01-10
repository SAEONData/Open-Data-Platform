from hydra_client import HydraTokenMixin

from odpaccounts.models import Base


class HydraToken(HydraTokenMixin, Base):
    """
    Represents the OAuth token for a user logged in locally to the admin service.
    """
    __tablename__ = 'odpadmin_token'
