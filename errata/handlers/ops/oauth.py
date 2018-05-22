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
from errata.utils.http import process_request


# OAuth hanlder client identifier.
OAUTH_CLIENT_ID = os.getenv('ERRATA_OAUTH_CLIENT_ID')

# OAuth hanlder client secret.
OAUTH_CLIENT_SECRET = os.getenv('ERRATA_OAUTH_CLIENT_SECRET')

# OAuth authorize URL.
OAUTH_URL_AUTHORIZE = 'https://github.com/login/oauth/authorize'

# OAuth get access token URL.
OAUTH_URL_ACCESS_TOKEN = 'https://github.com/login/oauth/access_token'

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
        # Open seesion with OAuth2 provider.
        github = OAuth2Session(OAUTH_CLIENT_ID)
        authorization_url, state = github.authorization_url(OAUTH_URL_AUTHORIZE)

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
        github = OAuth2Session(OAUTH_CLIENT_ID, state=self.get_secure_cookie('errata-oauth-state'))
        token = github.fetch_token(OAUTH_URL_ACCESS_TOKEN, client_secret=OAUTH_CLIENT_SECRET, authorization_response=self.request.full_url())

        # At this point you can fetch protected resources - we need the users GitHub ID.
        github = OAuth2Session(OAUTH_CLIENT_ID, token=token)
        gh_user = github.get('https://api.github.com/user').json()

        # Allow client side credential access via secure cookies.
        self.clear_cookie('errata-oauth-state')
        self.set_secure_cookie('errata-oauth-credentials', _encode_credentials(gh_user, token), expires_days=_COOKIE_EXPIRATION_IN_DAYS)
        print self.xsrf_token

        # Redirect.
        self.redirect('/static/index.html', permanent=False)


def _encode_credentials(user, token):
    """Encodes credentials for later use.

    """
    result = '{}:{}'.format(user['login'].strip(), token['access_token'].strip())

    return base64.encodestring(result)
