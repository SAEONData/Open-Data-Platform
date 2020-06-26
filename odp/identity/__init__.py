from flask_login import LoginManager
from flask_mail import Mail

from hydra import HydraAdminClient
from odp.db import session as db_session
from odp.db.models.user import User


login_manager = LoginManager()
login_manager.login_view = 'odpidentity.login'

mail = Mail()

hydra_admin = HydraAdminClient('')


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)
