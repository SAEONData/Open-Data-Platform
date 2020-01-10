from flask import current_app, abort


def hydra_error_abort(e):
    """
    Requests to the Hydra admin API are critical to the login, consent and logout flows.
    If anything is wrong with any response from Hydra, we abort - raising an internal
    server error.

    :param e: the HydraAdminError exception
    """
    current_app.logger.critical("Hydra server %d error for %s %s: %s",
                                e.status_code, e.method, e.endpoint, e.error_detail)
    abort(500)
