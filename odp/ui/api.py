from flask import abort
from requests import RequestException

from odp.config import config
from odp.ui.auth import oauth


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
            abort(e.response.status_code, e.response.text)
        else:
            abort(503, str(e))
