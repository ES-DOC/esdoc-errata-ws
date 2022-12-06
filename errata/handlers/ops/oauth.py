# -*- coding: utf-8 -*-

"""
.. module:: handlers.ops.oauth.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - OAuth handler.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import base64
import json
import os

import tornado
from requests_oauthlib import OAuth2Session

import errata
from errata.utils import config
from errata.utils import http_security
from errata.utils.http import process_request


# OAuth handler client identifier.
OAUTH_CLIENT_ID = os.getenv('ERRATA_OAUTH_CLIENT_ID')

# OAuth handler client secret.
OAUTH_CLIENT_SECRET = os.getenv('ERRATA_OAUTH_CLIENT_SECRET')

# OAuth authorize URL.
OAUTH_URL_AUTHORIZE = 'https://github.com/login/oauth/authorize'

# OAuth get access token URL.
OAUTH_URL_ACCESS_TOKEN = 'https://github.com/login/oauth/access_token'

# Application redirect URL.
APP_REDIRECT_URL = '/static/index.html'

# When in dev mode allow HTTP callback.
if config.mode == 'dev':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Time before oauth cookies expire = 0.042 = 1 hour.
_COOKIE_EXPIRATION_IN_DAYS = 0.042


class AuthorizeRequestHandler(tornado.web.RequestHandler):
    """OAuth begin request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        # Open session with OAuth2 provider.
        gh_session = OAuth2Session(OAUTH_CLIENT_ID, scope=("read:org", ))

        # Ask OAuth2 provider for an autohrisation URL.
        authorization_url, state = gh_session.authorization_url(OAUTH_URL_AUTHORIZE)

        # State is used to prevent CSRF, keep this for later.
        self.set_secure_cookie('errata-oauth-state', state, expires_days=_COOKIE_EXPIRATION_IN_DAYS)

        # Redirect.
        self.redirect(authorization_url, permanent=False)


class CallbackRequestHandler(tornado.web.RequestHandler):
    """OAuth callback request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        # The user has been redirected back from the OAuth provider.
        # With this redirection comes an authorization code included
        # in the redirect URL. We will use that to obtain an access token.
        gh_session = OAuth2Session(
            OAUTH_CLIENT_ID,
            state=self.get_secure_cookie('errata-oauth-state')
            )
        token = gh_session.fetch_token(
            OAUTH_URL_ACCESS_TOKEN,
            client_secret=OAUTH_CLIENT_SECRET,
            authorization_response=self.request.full_url()
            )

        # At this point you can fetch protected resources - we need the users GitHub ID.
        gh_session = OAuth2Session(OAUTH_CLIENT_ID, token=token)
        gh_user = gh_session.get('https://api.github.com/user').json()

        # Allow client side credential access via secure cookies.
        self.clear_cookie('errata-oauth-state')
        self.set_secure_cookie(
            'errata-oauth-credentials',
            _encode_credentials(gh_user, token),
            expires_days=_COOKIE_EXPIRATION_IN_DAYS
            )

        print(gh_user['login'].strip(), http_security.get_user_role(gh_user['login'].strip()))
        self.set_cookie(
            'errata-user-role',
            http_security.get_user_role(gh_user['login'].strip())
            )

        # Set XSRF header.
        self.set_header('X-XSRFToken', self.xsrf_token)            

        # Redirect.
        self.redirect(APP_REDIRECT_URL, permanent=False)


def _encode_credentials(user, token):
    """Encodes credentials for later use.

    """
    user_id = user['login'].strip()
    access_token = token['access_token'].strip()

    return base64.encodestring('{}:{}'.format(user_id, access_token))
