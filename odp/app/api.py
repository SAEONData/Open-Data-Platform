import httpx
from flask import abort

from odp.config import config


def get(url, **params):
    return _request('GET', url, params)


def _request(method, url, params):
    try:
        r = _client.request(method, url, params=params)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as e:
        abort(503, str(e))
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())


_client = httpx.Client(base_url=config.ODP.APP.API_URL)
