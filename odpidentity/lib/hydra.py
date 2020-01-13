from flask import current_app, redirect, url_for, flash


def hydra_error_page(e):
    """
    Requests to the Hydra admin API are critical to the login, consent and logout flows.
    If anything is wrong with any response from Hydra, we abort - redirecting the user
    home.

    :param e: the HydraAdminError exception
    """
    if 500 <= e.status_code < 600:
        current_app.logger.critical("Hydra server %d error for %s %s: %s",
                                    e.status_code, e.method, e.endpoint, e.error_detail)
    elif 400 <= e.status_code < 500:
        current_app.logger.error("Hydra client %d error for %s %s: %s",
                                 e.status_code, e.method, e.endpoint, e.error_detail)
    else:
        raise ValueError

    flash("There was a problem with your request. Our technicians have been notified.", category='error')
    return redirect(url_for('home.index'))
