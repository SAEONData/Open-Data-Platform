from functools import wraps

from authlib.integrations.base_client.errors import OAuthError
from flask import flash, url_for, redirect, request, g
from flask_login import current_user
from requests import RequestException

from odp import ODPScope
from odp.config import config
from odp.lib.auth import get_user_permissions
from odp.ui.auth import oauth


class ODPAPIError(Exception):
    def __init__(self, status_code, error_detail):
        self.status_code = status_code
        self.error_detail = error_detail


def get(path, **params):
    return _request('GET', path, None, params)


def post(path, data, **params):
    return _request('POST', path, data, params)


def put(path, data, **params):
    return _request('PUT', path, data, params)


def delete(path, **params):
    return _request('DELETE', path, None, params)


def _request(method, path, data, params):
    try:
        r = oauth.hydra.request(
            method,
            config.ODP.UI.API_URL + path,
            json=data,
            params=params,
        )
        r.raise_for_status()
        return r.json()

    except RequestException as e:
        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_detail = e.response.json()
            except ValueError:
                error_detail = e.response.text
        else:
            status_code = 503
            error_detail = str(e)

        raise ODPAPIError(status_code, error_detail) from e

    except OAuthError as e:
        raise ODPAPIError(401, str(e)) from e


def client(scope: ODPScope):
    """Decorator that configures a view as an API client with `scope`
    access, providing client-side authorization and API error handling."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access that page.')
                return redirect(url_for('home.index'))

            g.user_permissions = get_user_permissions(current_user.id, config.ODP.UI.CLIENT_ID)
            if scope not in g.user_permissions:
                flash('You do not have permission to access that page.', category='warning')
                return redirect(request.referrer)

            try:
                return f(*args, **kwargs)
            except ODPAPIError as e:
                return _handle_error(e)

        return decorated_function

    return decorator


def _handle_error(e: ODPAPIError):
    if e.status_code == 401:
        flash('An authentication error occurred. Please log in again to continue.', category='error')
        return redirect(url_for('hydra.logout'))

    if e.status_code == 403:
        flash('You do not have permission to access that page.', category='warning')
        return redirect(request.referrer)

    if e.status_code == 503:
        flash('Service unavailable. Please try again in a few minutes.', category='error')
        return redirect(url_for('home.index'))

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

    return redirect(request.referrer)
