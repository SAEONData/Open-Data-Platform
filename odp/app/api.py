import httpx
from flask import abort

from odp.config import config


def get(url, **params):
    return _request('GET', url, None, params)


def put(url, data, **params):
    return _request('PUT', url, data, params)


def delete(url, **params):
    return _request('DELETE', url, None, params)


def _request(method, url, data, params):
    try:
        r = _client.request(method, url, json=data, params=params)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as e:
        abort(503, str(e))
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())


_client = httpx.Client(
    base_url=config.ODP.APP.API_URL,
    timeout=None if config.ODP.ENV == 'development' else 5.0,
)
