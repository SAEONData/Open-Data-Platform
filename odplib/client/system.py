from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.requests_client import OAuth2Session


@dataclass
class ODPResponse:
    status: int
    content: Optional[Dict] = None
    error: Any = None


class OAuth2SystemClient:
    """A client for API access with a client credentials grant."""

    def __init__(
            self,
            api_url: str,
            token_url: str,
            client_id: str,
            client_secret: str,
            scope: list[str],
    ):
        self.api_url = api_url
        self.token = OAuth2Session(
            client_id=client_id,
            client_secret=client_secret,
            scope=' '.join(scope),
        ).fetch_token(
            url=token_url,
            grant_type='client_credentials',
            timeout=10.0,
        )

    def get(self, path, **params):
        return self._request('GET', path, None, params)

    def post(self, path, data, **params):
        return self._request('POST', path, data, params)

    def put(self, path, data, **params):
        return self._request('PUT', path, data, params)

    def delete(self, path, **params):
        return self._request('DELETE', path, None, params)

    def _request(self, method, path, data, params):
        try:
            r = requests.request(
                method=method,
                url=self.api_url + path,
                json=data,
                params=params,
                headers={
                    'Accept': 'application/json',
                    'Authorization': 'Bearer ' + self.token['access_token'],
                }
            )
            r.raise_for_status()

            return ODPResponse(
                status=r.status_code,
                content=r.json(),
            )

        except requests.RequestException as e:
            if e.response is not None:
                status = e.response.status_code
                try:
                    error = e.response.json()
                except ValueError:
                    error = e.response.text
            else:
                status = 503
                error = str(e)

            return ODPResponse(
                status=status,
                error=error,
            )

        except OAuthError as e:
            return ODPResponse(
                status=401,
                error=str(e),
            )
