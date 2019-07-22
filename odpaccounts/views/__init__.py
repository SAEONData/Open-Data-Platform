from flask_login import LoginManager

from . import home, user, hydra_client, hydra_auth
from ..models.user import User

login_manager = LoginManager()
login_manager.login_view = 'user.login'


def init_app(app):
    app.register_blueprint(home.bp, url_prefix='/')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(hydra_client.bp, url_prefix='/user')  # note: intentionally at /user
    app.register_blueprint(hydra_auth.bp, url_prefix='/auth')
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
