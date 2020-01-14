from flask import Blueprint
from flask_login import login_required

bp = Blueprint('user', __name__)


@bp.route('/profile')
@login_required
def profile():
    return 'User profile page'
