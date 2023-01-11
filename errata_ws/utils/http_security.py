from errata_ws.utils import config
from errata_ws.utils import constants
from errata_ws.utils import logger
from errata_ws.utils import security



# GitHub team names.
_GH_TEAM_PUBLICATION = 'errata-publication'
_GH_TEAM_MODERATION = 'errata-moderation'

# Set of endpoints accessible by anonymous users.
_WHITELISTED_ENDPOINTS = {
    '/',
    '/status',
    '/validate-dataset-id',
    '/verify-authorization',
    '/2/publication/propose',
    '/2/publication/retrieve',
    '/2/publication/retrieve-all',
    '/2/search/errata',
    '/2/search/errata/setup',
    '/1/pid-queue/search',
    '/1/pid-queue/search-setup',
    '/1/resolve/issue',
    '/1/resolve/pid',
    '/1/resolve/simple-pid'
}


def apply_policy(user_id, access_token, project_id, institute_id):
    """Applies security policy.

    :param str user_id: GitHub username.
    :param str access_token: GitHub access token.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    authenticate((user_id, access_token))
    authorize(user_id, project_id, institute_id)


def authenticate(credentials):
    """Authenticates user credentials request against GitHub user api.

    :param tuple credentials: 2 member tuple (GitHub username, GitHub access token)

    :returns: GitHub username
    :rtype: str

    """
    security.authenticate_user(credentials)


def authorize(user_id, project_id, institute_id):
    """Authorizes user against GitHub team membership api.

    :param str user_id: GitHub username.
    :param str project_id: Project identifier, e.g. cmip6.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    # Authorize moderators.
    try:
        # ... might be member of team: errata-moderation.
        logger.log_web('Authorizing: {} --> {}'.format(user_id, _GH_TEAM_MODERATION))
        security.authorize_user(_GH_TEAM_MODERATION, user_id)
    except security.AuthorizationError:
        pass
    else:
        return constants.USER_ROLE_MODERATOR

    # Authorize publishers.
    try:
        # ... must be member of team: errata-publication.
        logger.log_web('Authorizing: {} --> {}'.format(user_id, _GH_TEAM_PUBLICATION))
        security.authorize_user(_GH_TEAM_PUBLICATION, user_id)
        # ... must be member of team: {project}-{institute}.
        logger.log_web('Authorizing: {} --> {}-{}'.format(user_id, project_id, institute_id))
        security.authorize_user('{}-{}'.format(project_id, institute_id), user_id)
    except security.AuthorizationError as err:
        raise err
    else:
        return constants.USER_ROLE_AUTHOR


def authorize_moderation(user_id, project_id, institute_id):
    """Authorizes user against errata-moderation GitHub team membership api.

    :param str user_id: GitHub username.
    :param str project_id: Project identifier, e.g. cmip6.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    # User must be a member of errata-moderation team.
    logger.log_web('Authorizing: {} --> {}'.format(user_id, _GH_TEAM_MODERATION))
    security.authorize_user(_GH_TEAM_MODERATION, user_id)


def authorize_publication(user_id, project_id, institute_id):
    """Authorizes user against errata-publication GitHub team membership api.

    :param str user_id: GitHub username.
    :param str project_id: Project identifier, e.g. cmip6.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    # User must be a member of errata-publication team.
    logger.log_web('Authorizing: {} --> {}'.format(user_id, _GH_TEAM_PUBLICATION))
    security.authorize_user(_GH_TEAM_PUBLICATION, user_id)

    # User must be a member of {project}-{institute} specific team, e.g. cmip6-ipsl.
    logger.log_web('Authorizing: {} --> {}-{}'.format(user_id, project_id, institute_id))
    security.authorize_user('{}-{}'.format(project_id, institute_id), user_id)


def get_user_role(user_id):
    """Returns user's application role.

    :param str user_id: GitHub username.
    :returns: User role type.

    """
    try:
        security.authorize_user(_GH_TEAM_MODERATION, user_id)
    except security.AuthorizationError:
        try:
            security.authorize_user(_GH_TEAM_PUBLICATION, user_id)
        except security.AuthorizationError:
            return constants.USER_ROLE_ANONYMOUS
        else:
            return constants.USER_ROLE_AUTHOR
    else:
        return constants.USER_ROLE_MODERATOR


def secure_request(handler):
    """Enforces request level security policy (if necessary).

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.

    """
    # Escape if endpoint is whitelisted.
    if handler.request.path in _WHITELISTED_ENDPOINTS:
        return

    # Set credentials - either from web-form or cli client.
    credentials = handler.get_secure_cookie('errata-oauth-credentials') or \
                  handler.request.headers['Authorization']
    
    # Strip credentials - i.e. destructure from b64 --> 2 member tuple.
    credentials = security.strip_credentials(credentials)

    # Authenticate.
    if config.apply_security_policy:
        logger.log_web('Authenticating: {}'.format(credentials[0]))
        authenticate(credentials)
        logger.log_web('Authenticated: {}'.format(credentials[0]))

    # Make user-id available downstream.
    handler.user_id = credentials[0]


def set_headers(handler, is_post=False):
    """Set HTTP headers for an endpint.
    
    """
    handler.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")

    if is_post is True:
        handler.set_header('Access-Control-Allow-Methods', 'POST')

    if handler.request.path not in _WHITELISTED_ENDPOINTS:
        print(7777, handler.request.path)
        handler.set_header("Access-Control-Allow-Headers", "content-type, Authorization")
        handler.set_header('Access-Control-Allow-Credentials', True)
        handler.set_header('X-XSRFToken', handler.xsrf_token)
