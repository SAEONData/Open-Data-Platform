import requests
from authlib.integrations.requests_client import OAuth2Session

from odplib.client import ODPClient


class ODPSystemClient(ODPClient):
    """A client for ODP API access with a client credentials grant."""

    def __init__(
            self,
            api_url: str,
            hydra_url: str,
            client_id: str,
            client_secret: str,
            scope: list[str],
    ):
        super().__init__(api_url, hydra_url, client_id, client_secret, scope)
        self._token = None

    @property
    def token(self) -> dict:
        if self._token is None:
            self._token = OAuth2Session(
                client_id=self.client_id,
                client_secret=self.client_secret,
                scope=' '.join(self.scope),
            ).fetch_token(
                url=f'{self.hydra_url}/oauth2/token',
                grant_type='client_credentials',
                timeout=10.0,
            )
        return self._token

    def _send_request(self, method: str, url: str, data: dict, params: dict) -> requests.Response:
        return requests.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers={
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + self.token['access_token'],
            }
        )
