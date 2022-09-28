from flask import Blueprint, redirect, url_for

bp = Blueprint('hydra', __name__)


@bp.route('/signup')
def signup():
    from odplib.ui import odp_ui_client
    redirect_uri = url_for('.logged_in', _external=True)
    return odp_ui_client.login_redirect(redirect_uri, mode='signup')


@bp.route('/login')
def login():
    from odplib.ui import odp_ui_client
    redirect_uri = url_for('.logged_in', _external=True)
    return odp_ui_client.login_redirect(redirect_uri, mode='login')


@bp.route('/logged_in')
def logged_in():
    from odplib.ui import odp_ui_client
    odp_ui_client.login_callback()
    return redirect(url_for('home.index'))


@bp.route('/logout')
def logout():
    from odplib.ui import odp_ui_client
    redirect_uri = url_for('.logged_out', _external=True)
    return odp_ui_client.logout_redirect(redirect_uri)


@bp.route('/logged_out')
def logged_out():
    from odplib.ui import odp_ui_client
    odp_ui_client.logout_callback()
    return redirect(url_for('home.index'))
