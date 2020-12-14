import secrets
from typing import List

import redis
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, url_for, redirect, flash, request
from flask_login import login_user, logout_user, current_user
from sqlalchemy.orm.exc import NoResultFound

from odp.db import session as db_session
from odp.db.models import User, OAuth2Token


class HydraOAuth2Blueprint(Blueprint):
    """Blueprint for setting up a Flask app as an OAuth2 client to ORY Hydra.

    User-initiated routes::

        /signup
        /login
        /logout

    Hydra callback routes::

        /logged_in
        /logged_out
    """

    def __init__(
            self,
            name,
            import_name,
            server_url: str,
            client_id: str,
            client_secret: str,
            scope: List[str],
            verify_tls: bool,
            redirect_to: str,
            redis_host: str,
            redis_port: int,
            redis_db: int,
    ):
        """
        :param server_url: base URL of the Hydra public API
        :param client_id: client id
        :param client_secret: client secret
        :param scope: scope required by the client
        :param verify_tls: verify the Hydra server certificate
        :param redirect_to: the endpoint to which to redirect the user
            after login/logout has completed
        """
        super().__init__(name, import_name)
        self.cache = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        self.oauth = OAuth(
            cache=self.cache,
            fetch_token=self.fetch_token,
            update_token=self.update_token,
        )
        self.oauth.register(
            name='hydra',
            access_token_url=f'{server_url}/oauth2/token',
            authorize_url=f'{server_url}/oauth2/auth',
            userinfo_endpoint=f'{server_url}/userinfo',
            client_id=client_id,
            client_secret=client_secret,
            client_kwargs={'scope': ' '.join(scope)},
        )
        self.hydra_logout_url = f'{server_url}/oauth2/sessions/logout'
        self.verify_tls = verify_tls
        self.redirect_to = redirect_to

        # user-initiated routes
        self.add_url_rule('/signup', endpoint='signup', view_func=self.signup)
        self.add_url_rule('/login', endpoint='login', view_func=self.login)
        self.add_url_rule('/logout', endpoint='logout', view_func=self.logout)

        # callbacks
        self.add_url_rule('/logged_in', view_func=self.logged_in)
        self.add_url_rule('/logged_out', view_func=self.logged_out)

    def register(self, app, *args, **kwargs):
        super().register(app, *args, **kwargs)
        self.oauth.init_app(app)

    def signup(self):
        redirect_uri = url_for('.logged_in', _external=True)
        return self.oauth.hydra.authorize_redirect(redirect_uri, mode='signup')

    def login(self):
        redirect_uri = url_for('.logged_in', _external=True)
        return self.oauth.hydra.authorize_redirect(redirect_uri, mode='login')

    def logged_in(self):
        try:
            token = self.oauth.hydra.authorize_access_token(verify=self.verify_tls)
            userinfo = self.oauth.hydra.userinfo(verify=self.verify_tls)
            user_id = userinfo['sub']
            user = User.query.get(user_id)

            client_id = self.oauth.hydra.client_id
            try:
                token_model = OAuth2Token.query.filter_by(client_id=client_id, user_id=user_id).one()
            except NoResultFound:
                token_model = OAuth2Token(client_id=client_id, user_id=user_id)

            token_model.token_type = token.get('token_type')
            token_model.access_token = token.get('access_token')
            token_model.refresh_token = token.get('refresh_token')
            token_model.id_token = token.get('id_token')
            token_model.expires_at = token.get('expires_at')
            token_model.save()
            # todo: handle commit/rollback in framework
            db_session.commit()

            login_user(user)

        except OAuthError as e:
            flash(str(e), category='error')

        return redirect(url_for(self.redirect_to))

    def logout(self):
        token = self.fetch_token(self.oauth.hydra.client_id)
        state_val = secrets.token_urlsafe()
        self.cache.set(self.state_key(), state_val, ex=10)
        url = f'{self.hydra_logout_url}?id_token_hint={token.get("id_token")}' \
              f'&post_logout_redirect_uri={url_for(".logged_out", _external=True)}' \
              f'&state={state_val}'
        return redirect(url)

    def logged_out(self):
        state_val = request.args.get('state')
        if state_val == self.cache.get(state_key := self.state_key()):
            logout_user()
            self.cache.delete(state_key)
        return redirect(url_for(self.redirect_to))

    def state_key(self):
        return f'{self.__module__}.{self.__class__.__name__}' \
               f'_{self.oauth.hydra.client_id}_{current_user.id}_state'

    @staticmethod
    def fetch_token(client_id):
        return OAuth2Token.query.filter_by(client_id=client_id, user_id=current_user.id).one().dict()

    @staticmethod
    def update_token(client_id, token, refresh_token=None, access_token=None):
        if refresh_token:
            token_model = OAuth2Token.query.filter_by(client_id=client_id, refresh_token=refresh_token).one()
        elif access_token:
            token_model = OAuth2Token.query.filter_by(client_id=client_id, access_token=access_token).one()
        else:
            return

        token_model.access_token = token.get('access_token')
        token_model.refresh_token = token.get('refresh_token')
        token_model.expires_at = token.get('expires_at')
        token_model.save()
        # todo: handle commit/rollback in framework
        db_session.commit()
