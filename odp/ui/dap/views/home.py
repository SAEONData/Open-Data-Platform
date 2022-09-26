from flask import Blueprint, render_template

from odplib.config import config

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    return render_template('home.html', thredds_url=config.ODP.UI.DAP.THREDDS_URL)
