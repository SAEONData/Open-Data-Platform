from flask_login import LoginManager

from . import home, auth, user, hydra
from ..models.user import User

login_manager = LoginManager()
login_manager.login_view = 'user.login'


def init_app(app):
    app.register_blueprint(home.bp, url_prefix='/')
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(hydra.bp, url_prefix='/user')  # note: intentionally at /user
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
