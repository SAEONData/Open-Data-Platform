from functools import wraps
from typing import Callable

from flask import Flask, current_app, flash, g, redirect, request, url_for
from flask_login import current_user

from odp import ODPScope
from odp.lib.auth import get_user_permissions
from odplib.client import ODPAPIError

get: Callable
post: Callable
put: Callable
delete: Callable


def init_app(app: Flask):
    from odplib.ui import odp_ui_client
    global get, post, put, delete
    get = odp_ui_client.get
    post = odp_ui_client.post
    put = odp_ui_client.put
    delete = odp_ui_client.delete


def client(*scope: ODPScope, fallback_to_referrer=False):
    """Decorator that configures a view as an API client requiring any of
    the given `scope` for API access. It provides client-side authorization
    and API error handling.

    If `fallback_to_referrer` is True, then after an unhandled API error the
    user lands back on the same page they were on. Otherwise (by default),
    they are redirected to the blueprint's index view.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access that page.')
                return redirect(url_for('home.index'))

            g.user_permissions = get_user_permissions(current_user.id, current_app.config['CLIENT_ID'])
            if not any(s in g.user_permissions for s in scope):
                flash('You do not have permission to access that page.', category='warning')
                return redirect(request.referrer or url_for('home.index'))

            try:
                # call the view function
                return f(*args, **kwargs)

            except ODPAPIError as e:
                if response := handle_error(e):
                    return response

                if e.status_code == 503:
                    # avoid redirect loops when the API is unavailable
                    return redirect(url_for('home.index'))

                if fallback_to_referrer and request.referrer:
                    return redirect(request.referrer)

                # fall back to the index page
                return redirect(url_for('.index'))

        return decorated_function

    return decorator


def handle_error(e: ODPAPIError):
    """For authentication and authorization errors we bail out and return
    an appropriate redirect. For any other kind of error, we just display
    the error message and let the caller decide what to do."""

    if e.status_code == 401:
        flash('Your session has expired. Please log in again to continue.', category='error')
        return redirect(url_for('hydra.logout'))

    if e.status_code == 403:
        flash('You do not have permission to access that page.', category='warning')
        return redirect(request.referrer or url_for('home.index'))

    if e.status_code == 503:
        flash('Service unavailable. Please try again in a few minutes.', category='error')
        return

    try:
        detail = e.error_detail['detail']
        if e.status_code == 422 and isinstance(detail, list):
            # duplicate validation errors are returned when multiple
            # server-side dependencies validate the same input; we
            # eliminate duplicates by packing them into a dict
            errors = {
                error['loc'][1]: error['msg']
                for error in detail
            }
            for field, msg in errors.items():
                flash(f'{field}: {msg}', category='error')
        else:
            flash(detail, category='error')

    except (TypeError, KeyError, IndexError):
        flash(e.error_detail, category='error')
