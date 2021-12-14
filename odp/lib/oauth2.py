import secrets

from authlib.integrations.flask_client import OAuth
from flask import redirect, request
from flask_login import current_user, login_user, logout_user
from redis import Redis
from sqlalchemy import select

from odp.db import Session
from odp.db.models import OAuth2Token, User


class FlaskOAuth2Client:
    def __init__(
            self,
            hydra_url: str,
            client_id: str,
            client_secret: str,
            scope: list[str],
            cache: Redis,
    ):
        self.hydra_url = hydra_url
        self.client_id = client_id
        self.oauth = OAuth(cache=cache, fetch_token=self._fetch_token, update_token=self._update_token)
        self.oauth.register(
            name='hydra',
            access_token_url=f'{hydra_url}/oauth2/token',
            authorize_url=f'{hydra_url}/oauth2/auth',
            userinfo_endpoint=f'{hydra_url}/userinfo',
            client_id=client_id,
            client_secret=client_secret,
            client_kwargs={'scope': ' '.join(scope)},
        )

    def init_app(self, app):
        self.oauth.init_app(app)

    def login_redirect(self, redirect_uri, **kwargs):
        """Return a redirect to the Hydra authorization endpoint."""
        return self.oauth.hydra.authorize_redirect(redirect_uri, **kwargs)

    def login_callback(self):
        """Save the token and log the user in."""
        token = self.oauth.hydra.authorize_access_token()
        userinfo = self.oauth.hydra.userinfo()
        user_id = userinfo['sub']

        if not (token_model := Session.get(OAuth2Token, (self.client_id, user_id))):
            token_model = OAuth2Token(client_id=self.client_id, user_id=user_id)

        token_model.token_type = token.get('token_type')
        token_model.access_token = token.get('access_token')
        token_model.refresh_token = token.get('refresh_token')
        token_model.id_token = token.get('id_token')
        token_model.expires_at = token.get('expires_at')
        token_model.save()

        user = Session.get(User, user_id)
        login_user(user)

    def logout_redirect(self, redirect_uri):
        """Return a redirect to the Hydra endsession endpoint."""
        token = self.oauth.fetch_token('hydra')
        state_val = secrets.token_urlsafe()
        self.oauth.cache.set(self._state_key(), state_val, ex=10)
        url = f'{self.hydra_url}/oauth2/sessions/logout' \
              f'?id_token_hint={token.get("id_token")}' \
              f'&post_logout_redirect_uri={redirect_uri}' \
              f'&state={state_val}'
        return redirect(url)

    def logout_callback(self):
        """Log the user out."""
        state_val = request.args.get('state')
        if state_val == self.oauth.cache.get(key := self._state_key()):
            logout_user()
            self.oauth.cache.delete(key)

    def request(self, method, url, **kwargs):
        """Make a request with the user's access token."""
        return self.oauth.hydra.request(method, url, **kwargs)

    def _state_key(self):
        return f'{__name__}.{self.client_id}.{current_user.id}.state'

    def _fetch_token(self, hydra):
        return Session.get(OAuth2Token, (self.client_id, current_user.id)).dict()

    def _update_token(self, hydra, token, refresh_token=None, access_token=None):
        if refresh_token:
            token_model = Session.execute(
                select(OAuth2Token).
                where(OAuth2Token.client_id == self.client_id).
                where(OAuth2Token.refresh_token == refresh_token)
            ).scalar_one()
        elif access_token:
            token_model = Session.execute(
                select(OAuth2Token).
                where(OAuth2Token.client_id == self.client_id).
                where(OAuth2Token.access_token == access_token)
            ).scalar_one()
        else:
            return

        token_model.access_token = token.get('access_token')
        token_model.refresh_token = token.get('refresh_token')
        token_model.expires_at = token.get('expires_at')
        token_model.save()
