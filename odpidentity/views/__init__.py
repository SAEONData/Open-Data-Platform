from flask_login import LoginManager

from odpaccounts.db import session as db_session
from odpaccounts.models.user import User

login_manager = LoginManager()
login_manager.login_view = 'oauth2.login'


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)


def init_app(app):
    login_manager.init_app(app)

    from . import home, user, hydra_oauth2, hydra_integration
    app.register_blueprint(home.bp, url_prefix='/')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(hydra_oauth2.bp, url_prefix='/oauth2')
    app.register_blueprint(hydra_integration.bp, url_prefix='/hydra')
