from odp.db import session as db_session
from odp.db.models.user import User
from odp.db.models.oauth2_token import OAuth2Token
from hydra_oauth2 import HydraOAuth2Blueprint

# Note: the blueprint name 'odpidentity' becomes the provider in the token model
bp = HydraOAuth2Blueprint('odpidentity', __name__, db_session, User, OAuth2Token, 'home.index')
