from hydra_client import HydraTokenMixin

from . import Base


class HydraToken(HydraTokenMixin, Base):
    """
    Represents the OAuth token for a user logged in locally to the identity service.
    """
