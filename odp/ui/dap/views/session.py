from flask import Blueprint, abort
from flask_login import current_user

bp = Blueprint('session', __name__)


@bp.route('/check')
def check_session():
    if not current_user.is_authenticated:
        abort(401)

    return {
        'subject': current_user.id,
        'extra': {},
    }
