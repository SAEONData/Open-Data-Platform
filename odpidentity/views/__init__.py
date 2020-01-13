from flask_login import LoginManager
from flask_mail import Mail
from flask.helpers import get_env

from hydra import HydraAdminClient
from odpaccounts.db import session as db_session
from odpaccounts.models.user import User

login_manager = LoginManager()
login_manager.login_view = 'odpidentity.login'

mail = Mail()

hydra_admin = None


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)


def init_app(app):
    login_manager.init_app(app)
    mail.init_app(app)

    global hydra_admin
    hydra_admin = HydraAdminClient(
        server_url=app.config['HYDRA_ADMIN_URL'],
        remember_login_for=app.config['HYDRA_LOGIN_EXPIRY'],
        verify_tls=get_env() != 'development',
    )

    from . import home, user, hydra_oauth2, hydra_integration
    app.register_blueprint(home.bp, url_prefix='/')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(hydra_oauth2.bp, url_prefix='/oauth2')
    app.register_blueprint(hydra_integration.bp, url_prefix='/hydra')
