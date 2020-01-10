from hydra_client import HydraTokenMixin

from odpaccounts.models import Base


class HydraToken(HydraTokenMixin, Base):
    """
    Represents the OAuth token for a user logged in locally to the identity service.
    """
    __tablename__ = 'odpidentity_token'
