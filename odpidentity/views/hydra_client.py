from ..models import db
from ..models.user import User
from ..models.hydra_token import HydraToken

from hydra_client import HydraClientBlueprint

bp = HydraClientBlueprint('hydra', __name__, db, User, HydraToken)
