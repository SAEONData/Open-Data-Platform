from flask import Blueprint, redirect, url_for

from odp_uilib.auth import oauth2

bp = Blueprint('hydra', __name__)


@bp.route('/signup')
def signup():
    redirect_uri = url_for('.logged_in', _external=True)
    return oauth2.login_redirect(redirect_uri, mode='signup')


@bp.route('/login')
def login():
    redirect_uri = url_for('.logged_in', _external=True)
    return oauth2.login_redirect(redirect_uri, mode='login')


@bp.route('/logged_in')
def logged_in():
    oauth2.login_callback()
    return redirect(url_for('home.index'))


@bp.route('/logout')
def logout():
    redirect_uri = url_for('.logged_out', _external=True)
    return oauth2.logout_redirect(redirect_uri)


@bp.route('/logged_out')
def logged_out():
    oauth2.logout_callback()
    return redirect(url_for('home.index'))
