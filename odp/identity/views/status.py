from flask import Blueprint

bp = Blueprint('status', __name__)


@bp.route('/')
def status():
    """Check whether the identity service is alive."""
    return "OK"
