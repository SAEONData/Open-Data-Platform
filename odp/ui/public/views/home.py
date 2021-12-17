from flask import Blueprint, render_template

from odp.config import config

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    return render_template('home.html', thredds_url=config.ODP.UI.PUBLIC.THREDDS_URL)
