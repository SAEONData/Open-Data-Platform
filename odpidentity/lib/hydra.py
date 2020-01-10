from flask import current_app, abort
from flask.helpers import get_env

from hydra import HydraAdminClient


def create_hydra_admin():
    """
    Returns a HydraAdminClient instance.
    """
    return HydraAdminClient(
        server_url=current_app.config['HYDRA_ADMIN_URL'],
        remember_login_for=current_app.config['HYDRA_LOGIN_EXPIRY'],
        verify_tls=get_env() != 'development',
    )


def hydra_error(e):
    """
    Requests to the Hydra admin API are critical to the login, consent and logout flows.
    If anything is wrong with any response from Hydra, we abort - raising an internal
    server error.

    :param e: the HydraAdminError exception
    """
    current_app.logger.critical("Hydra server %d error for %s %s: %s",
                                e.status_code, e.method, e.endpoint, e.error_detail)
    abort(500)
