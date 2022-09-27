from flask import Blueprint, redirect, url_for

from odplib.ui.auth import oauth2_ui_client

bp = Blueprint('hydra', __name__)


@bp.route('/signup')
def signup():
    redirect_uri = url_for('.logged_in', _external=True)
    return oauth2_ui_client.login_redirect(redirect_uri, mode='signup')


@bp.route('/login')
def login():
    redirect_uri = url_for('.logged_in', _external=True)
    return oauth2_ui_client.login_redirect(redirect_uri, mode='login')


@bp.route('/logged_in')
def logged_in():
    oauth2_ui_client.login_callback()
    return redirect(url_for('home.index'))


@bp.route('/logout')
def logout():
    redirect_uri = url_for('.logged_out', _external=True)
    return oauth2_ui_client.logout_redirect(redirect_uri)


@bp.route('/logged_out')
def logged_out():
    oauth2_ui_client.logout_callback()
    return redirect(url_for('home.index'))
