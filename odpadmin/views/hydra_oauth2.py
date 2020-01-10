from odpaccounts.db import session as db_session
from odpaccounts.models.user import User
from hydra_client import HydraClientBlueprint

from ..models.hydra_token import HydraToken

bp = HydraClientBlueprint('oauth2', __name__, db_session, User, HydraToken)
