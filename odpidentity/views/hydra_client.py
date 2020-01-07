from ..models import db_session
from ..models.user import User
from ..models.hydra_token import HydraToken

from hydra_client import HydraClientBlueprint

bp = HydraClientBlueprint('hydra', __name__, db_session, User, HydraToken)
