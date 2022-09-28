from typing import Any, Optional

import requests
from authlib.integrations.base_client.errors import OAuthError


class ODPAPIError(Exception):
    def __init__(self, status_code, error_detail):
        self.status_code = status_code
        self.error_detail = error_detail


class ODPClient:
    """Base class for ODP API access using an authorized OAuth2 client."""

    def __init__(
            self,
            api_url: str,
            hydra_url: str,
            client_id: str,
            client_secret: str,
            scope: list[str],
    ) -> None:
        self.api_url = api_url
        self.hydra_url = hydra_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope

    def get(self, path: str, **params: Any) -> Any:
        return self.request('GET', path, None, **params)

    def post(self, path: str, data: dict, **params: Any) -> Any:
        return self.request('POST', path, data, **params)

    def put(self, path: str, data: dict, **params: Any) -> Any:
        return self.request('PUT', path, data, **params)

    def delete(self, path: str, **params: Any) -> Any:
        return self.request('DELETE', path, None, **params)

    def request(
            self,
            method: str,
            path: str,
            data: Optional[dict],
            **params: Any,
    ) -> Any:
        try:
            r = self._send_request(method, self.api_url + path, data, params)
            r.raise_for_status()
            return r.json()

        except requests.RequestException as e:
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

    def _send_request(self, method: str, url: str, data: dict, params: dict) -> requests.Response:
        raise NotImplementedError
