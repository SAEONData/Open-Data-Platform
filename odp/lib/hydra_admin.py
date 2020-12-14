from typing import List

import requests

from odp.lib.exceptions import HydraAdminError


class HydraAdminClient:
    """ A client for the ORY Hydra admin API """

    def __init__(
            self,
            server_url: str,
            verify_tls: bool = True,
            timeout: float = 5.0,
            remember_login_for: int = 30 * 86400,  # 30 days
            remember_consent_for: int = 0,
    ):
        """
        Constructor.

        :param server_url: the base URL of the Hydra admin API
        :param verify_tls: whether to verify the Hydra server TLS certificate
        :param timeout: how long to wait for data from Hydra (seconds)
        :param remember_login_for: number of seconds to remember a successful login; 0 = remember indefinitely
        :param remember_consent_for: number of seconds to remember a successful consent; 0 = remember indefinitely
        """
        self.server_url = server_url
        self.verify_tls = verify_tls
        self.timeout = timeout
        self.remember_login_for = remember_login_for
        self.remember_consent_for = remember_consent_for

    def get_login_request(
            self,
            login_challenge: str,
    ) -> dict:
        """
        Fetch information about an OAuth2 login request from Hydra. This should be called by
        the login provider after being redirected to the login endpoint from Hydra.

        https://www.ory.sh/hydra/docs/reference/api/#get-a-login-request
        https://www.ory.sh/hydra/docs/reference/api/#schemaloginrequest

        :param login_challenge: the value of the 'login_challenge' param in the login URL
        :return: dict
        """
        return self._request('GET', '/oauth2/auth/requests/login', params={'login_challenge': login_challenge})

    def accept_login_request(
            self,
            login_challenge: str,
            user_id: str,
    ) -> str:
        """
        Inform Hydra that the user has successfully authenticated, and return a redirect URL
        which the login provider should redirect to next.

        https://www.ory.sh/hydra/docs/reference/api/#accept-a-login-request

        :param login_challenge: the value of the 'login_challenge' param in the login URL
        :param user_id: the id of the authenticated user
        :return: str
        """
        r = self._request('PUT', '/oauth2/auth/requests/login/accept',
                          params={'login_challenge': login_challenge},
                          json={
                              'subject': user_id,
                              'remember': True,
                              'remember_for': self.remember_login_for,
                          })
        return r['redirect_to']

    def reject_login_request(
            self,
            login_challenge: str,
            error_code: str,
            error_description: str,
    ) -> str:
        """
        Inform Hydra that the user has not authenticated, and return a redirect URL which the
        login provider should redirect to next.

        https://www.ory.sh/hydra/docs/reference/api/#reject-a-login-request

        :param login_challenge: the value of the 'login_challenge' param in the login URL
        :param error_code: a short string representing the error
        :param error_description: a more detailed description of the error
        :return: str
        """
        r = self._request('PUT', '/oauth2/auth/requests/login/reject',
                          params={'login_challenge': login_challenge},
                          json={
                              'error': error_code,
                              'error_description': error_description,
                          })
        return r['redirect_to']

    def get_consent_request(
            self,
            consent_challenge: str,
    ) -> dict:
        """
        Fetch information about an OAuth2 consent request from Hydra. This should be called by
        the consent provider after being redirected to the consent endpoint from Hydra.

        https://www.ory.sh/hydra/docs/reference/api/#get-consent-request-information
        https://www.ory.sh/hydra/docs/reference/api/#schemaconsentrequest

        :param consent_challenge: the value of the 'consent_challenge' param in the consent URL
        :return: dict
        """
        return self._request('GET', '/oauth2/auth/requests/consent', params={'consent_challenge': consent_challenge})

    def accept_consent_request(
            self,
            consent_challenge: str,
            grant_scope: List[str],
            grant_audience: List[str],
            access_token_data: dict,
            id_token_data: dict,
    ) -> str:
        """
        Inform Hydra that the user has authorized the OAuth2 client to access resources on his/her
        behalf, and return a redirect URL which the consent provider should redirect to next.

        https://www.ory.sh/hydra/docs/reference/api/#accept-a-consent-request

        :param consent_challenge: the value of the 'consent_challenge' param in the consent URL
        :param grant_scope: list of scopes authorized for the client; should be a subset of
            'requested_scope' in the consent request
        :param grant_audience: list of audiences authorized for the client; should be a subset of
            'requested_access_token_audience' in the consent request
        :param access_token_data: data to be included in the access token
        :param id_token_data: data to be included in the ID token
        :return: str
        """
        r = self._request('PUT', '/oauth2/auth/requests/consent/accept',
                          params={'consent_challenge': consent_challenge},
                          json={
                              'grant_scope': grant_scope,
                              'grant_access_token_audience': grant_audience,
                              'remember': True,
                              'remember_for': self.remember_consent_for,
                              'session': {
                                  'access_token': access_token_data,
                                  'id_token': id_token_data,
                              },
                          })
        return r['redirect_to']

    def reject_consent_request(
            self,
            consent_challenge: str,
            error_code: str,
            error_description: str,
    ) -> str:
        """
        Inform Hydra that the user has *not* authorized the OAuth2 client to access resources on his/her
        behalf, and return a redirect URL which the consent provider should redirect to next.

        https://www.ory.sh/hydra/docs/reference/api/#reject-a-consent-request

        :param consent_challenge: the value of the 'consent_challenge' param in the consent URL
        :param error_code: a short string representing the error
        :param error_description: a more detailed description of the error
        :return: str
        """
        r = self._request('PUT', '/oauth2/auth/requests/consent/reject',
                          params={'consent_challenge': consent_challenge},
                          json={
                              'error': error_code,
                              'error_description': error_description,
                          })
        return r['redirect_to']

    def get_logout_request(
            self,
            logout_challenge: str,
    ) -> dict:
        """
        Fetch information about an OAuth2 logout request from Hydra. This should be called by
        the logout provider after being redirected to the logout endpoint from Hydra.

        https://www.ory.sh/hydra/docs/reference/api/#get-a-logout-request
        https://www.ory.sh/hydra/docs/reference/api/#schemalogoutrequest

        :param logout_challenge: the value of the 'logout_challenge' param in the logout URL
        :return: dict
        """
        return self._request('GET', '/oauth2/auth/requests/logout', params={'logout_challenge': logout_challenge})

    def accept_logout_request(
            self,
            logout_challenge: str,
    ) -> str:
        """
        Confirm a logout with Hydra, and return a redirect URL which the logout provider
        should redirect to next.

        https://www.ory.sh/hydra/docs/reference/api/#accept-a-logout-request

        :param logout_challenge: the value of the 'logout_challenge' param in the logout URL
        :return: str
        """
        r = self._request('PUT', '/oauth2/auth/requests/logout/accept',
                          params={'logout_challenge': logout_challenge},
                          )
        return r['redirect_to']

    def reject_logout_request(
            self,
            logout_challenge: str,
            error_code: str,
            error_description: str,
    ) -> None:
        """
        Deny a logout request with Hydra.

        https://www.ory.sh/hydra/docs/reference/api/#reject-a-logout-request

        :param logout_challenge: the value of the 'logout_challenge' param in the logout URL
        :param error_code: a short string representing the error
        :param error_description: a more detailed description of the error
        """
        self._request('PUT', '/oauth2/auth/requests/logout/reject',
                      params={'logout_challenge': logout_challenge},
                      json={
                          'error': error_code,
                          'error_description': error_description,
                      })

    def introspect_token(
            self,
            token: str,
            require_scope: List[str] = None,
            require_audience: List[str] = None,
    ) -> dict:
        """
        Validate an OAuth2 access/refresh token and return additional information about the token.

        https://www.ory.sh/hydra/docs/reference/api/#introspect-oauth2-tokens
        https://www.ory.sh/hydra/docs/reference/api/#schemaoauth2tokenintrospection

        :param token: opaque access/refresh token string
        :param require_scope: (optional) list of scopes that the token is expected to be valid for
        :param require_audience: (optional) list of audiences that the token is expected to be valid for
        :return: dict
        """
        token_info = self._request('POST', '/oauth2/introspect',
                                   headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                   data={
                                       'token': token,
                                       'scope': ' '.join(require_scope) if require_scope is not None else None,
                                   })
        if token_info['active']:
            if require_audience is not None and not (set(require_audience) <= set(token_info.get('aud', []))):
                token_info = {'active': False}

        return token_info

    def _request(self, method, endpoint, **kwargs):
        headers = {'Accept': 'application/json'}
        if method in ('POST', 'PUT'):
            headers['Content-Type'] = 'application/json'
        headers.update(kwargs.pop('headers', {}))

        e_kwargs = {'method': method, 'endpoint': endpoint}
        try:
            r = requests.request(method, self.server_url + endpoint, **kwargs,
                                 verify=self.verify_tls,
                                 timeout=self.timeout,
                                 headers=headers,
                                 )
            r.raise_for_status()
            return r.json()

        except requests.HTTPError as e:
            e_kwargs['status_code'] = e.response.status_code
            try:
                e_kwargs['error_detail'] = e.response.json()
            except ValueError:
                pass
            raise HydraAdminError(*e.args, **e_kwargs) from e

        except requests.RequestException as e:
            e_kwargs['status_code'] = 503
            raise HydraAdminError(*e.args, **e_kwargs) from e
