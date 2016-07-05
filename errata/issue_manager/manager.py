# -*- coding: utf-8 -*-

"""
.. module:: errata.issue_manager.manager.py
   :platform: Unix
   :synopsis: Manages ESGF issue onto ES-DOC

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""

# TODO : Convert close option as update to "Resolved" workflow value
# TODO : Add delete action giving issue id, controlled by GitHub roles
# TODO : Discuss Handle Service connection/authentication only by ES-DOC from Errata Service

# Module imports
import os
import sys
import uuid
import logging
from esgfpid import ESGF_PID_connector
from issue_handler import ESGFIssue, GitHubIssue
from utils import config_parse, init_logging, split_line
from github3 import GitHub


def github_connector(username, password, team, repo):
    """
    Instantiates the GitHub repository connector if granted for user.

    :param username: The GitHub login
    :param password: The GitHub password
    :param team: The GitHub team to connect
    :param repo: The GitHub repository to reach
    :returns: The GitHub repository connector and the GitHub user login
    :rtype: *tuple* of (*str*, *github3.repos.repo*)
    :raises Error: If the GitHub connection fails because of invalid inputs

    """
    logging.info('Connection to the GitHub repository "{0}/{1}"'.format(team, repo.lower()))
    try:
        gh_user = GitHub(username, password)
        gh_repo = gh_user.repository(team, repo.lower())
        logging.info('Result: SUCCESSFUL')
        return username, gh_repo
    except:
        logging.exception('Result: FAILED // Access denied')
        sys.exit(1)


def pid_connector(prefix, url_messaging_service, messaging_exchange, rabbit_username,
                  rabbit_password, successful_messages=True):
    """
    Instantiates the PID Handle Service connector if granted for user.

    :param str prefix: The PID prefix to use
    :param str url_messaging_service: The Handle Service URL
    :param str messaging_exchange: The message header
    :param str rabbit_username: The RabbitMQ username
    :param str rabbit_password: The RabbitMQ password
    :param boolean successful_messages: True to store successful messages
    :returns: The Handle Service connector
    :rtype: *ESGF_PID_connector*
    :raises Error: If the Handle Service connection fails because of invalid inputs

    """
    logging.info('Connection to the RabbitMQ Server of the Handle Service')
    try:
        if not os.path.isdir(__UNSENT_MESSAGES_DIR__):
            os.mkdir(__UNSENT_MESSAGES_DIR__)
        pid = ESGF_PID_connector(prefix=prefix,
                                 url_messaging_service=url_messaging_service,
                                 messaging_exchange=messaging_exchange,
                                 data_node='foo.fr',
                                 thredds_service_path='/what/ever/',
                                 solr_url='http://i-will.not/be/used',
                                 rabbit_username=rabbit_username,
                                 rabbit_password=rabbit_password,
                                 directory_unsent_messages=__UNSENT_MESSAGES_DIR__,
                                 store_successful_messages=successful_messages)
        logging.info('Result: SUCCESSFUL')
        return pid
    except:
        logging.exception('Result: FAILED // Access denied')
        sys.exit(1)


def get_projects(config):
    """
    Gets project options from esg.ini file.

    :param dict config: The configuration file parser
    :returns: The project options
    :rtype: *list*

    """
    project_options = split_line(config.get('DEFAULT', 'project_options'), sep='\n')
    return [option[0].upper() for option in map(lambda x: split_line(x), project_options[1:])]


def get_descriptions(gh):
    """
    Gets description strings from all registered GitHub issues.

    :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
    :returns: The descriptions strings and associated issue numbers
    :rtype: *dict*
    :raises Error: If retrieval fails without any results

    """
    descriptions = {}
    issues = gh.iter_issues(state='all')
    if issues:
        for issue in issues:
            content = GitHubIssue.issue_content_parser(issue.body)
            descriptions[issue.number] = content['description']
        return descriptions
    else:
        raise Exception('Cannot retrieve all descriptions from GitHub repository')


def get_number(gh, id):
    """
    Gets issue number depending on ESGF id.

    :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
    :param str id: The ESGF id
    :returns: The corresponding issue number
    :rtype: *int*
    :raises Error: If retrieval fails without any results

    """
    if not isinstance(id, uuid.UUID):
        return id
    issues = gh.iter_issues(state='all')
    if issues:
        for issue in issues:
            content = GitHubIssue.issue_content_parser(issue.body)
            if id == content['id']:
                return issue.number
    else:
        raise Exception('Cannot retrieve all ESGF IDs from GitHub repository')


def run():
    """
    Main process that\:
     * Parse command-line arguments,
     * Parse configuration file,
     * Initiates logger,
     * Check GitHub permissions,
     * Check Handle Service connection,
     * Run the issue action.

    """
    # Get command-line arguments
    args = get_args()
    # Parse configuration INI file
    cfg = config_parse(args.i)
    # Init logging
    if args.v:
        init_logging(args.log, level='DEBUG')
    elif cfg.has_option('initialize', 'log_level'):
        init_logging(args.log, cfg.get('initialize', 'log_level'))
    else:
        init_logging(args.log)
    # Connection to the GitHub repository
    gh_login, gh = github_connector(username=cfg.get('issues', 'gh_login'),
                                    password=cfg.get('issues', 'gh_password'),
                                    team=cfg.get('issues', 'gh_team'),
                                    repo=cfg.get('issues', 'gh_repo'))
    # Connection to the Handle Service
    hs = pid_connector(prefix=cfg.get('issues', 'prefix'),
                       url_messaging_service=cfg.get('issues', 'url_messaging_service'),
                       messaging_exchange=cfg.get('issues', 'messaging_exchange'),
                       rabbit_username=cfg.get('issues', 'rabbit_username'),
                       rabbit_password=cfg.get('issues', 'rabbit_password'))
    # Run command



def create_issue(issue, dsets):
    """Given a JSON file and a list of dataset IDs, this will create the issue entry.

    :param issue: Handle identifier
    :return: errata information, dset/file_id
    """
    # Instantiate issue class from issue template and datasets list
    submitted_issue = ESGFIssue(issue, dsets)
    # Validate ESGF issue against JSON schema
    submitted_issue.validate('create')
    # Create ESGF issue on GitHub repository
    submitted_issue.create(gh=gh, assignee=gh_login, descriptions=get_descriptions(gh))
    # Send issue id to Handle Service
    # TODO : Uncomment for master release
    # #submitted_issue.send(hs, gh_repo.name)

def update_issue(issue, dsets):
    """Given a JSON file and a list of dataset IDs, this will create the issue entry.

    :param issue: Handle identifier
    :return: errata information, dset/file_id
    """        # Instantiate ESGF issue from issue template and datasets list
    local_issue = ESGFIssue(issue_f=args.issue,
                            dsets_f=args.dsets)
    # Validate ESGF issue against JSON schema
    local_issue.validate(action=args.command,
                         projects=get_projects(cfg))
    # Get corresponding GitHub issue
    remote_issue = GitHubIssue(gh=gh,
                               number=local_issue.get('number'))
    # Validate GitHub issue against JSON schema
    remote_issue.validate(action=args.command,
                          projects=get_projects(cfg))
    # Update ESGF issue information on GitHub repository
    local_issue.update(gh=gh,
                       remote_issue=remote_issue)
    # Update issue id to Handle Service
    # TODO : Uncomment for master release
    #local_issue.send(hs, gh_repo.name)

def close_issue(issue, dsets):
    """Given a JSON file and a list of dataset IDs, this will create the issue entry.

    :param issue: Handle identifier
    :return: errata information, dset/file_id
    """
    # Instantiate ESGF issue from issue template and datasets list
    local_issue = ESGFIssue(issue_f=args.issue,
                            dsets_f=args.dsets)
    # Validate ESGF issue against JSON schema
    local_issue.validate(action=args.command,
                         projects=get_projects(cfg))
    # Get corresponding GitHub issue
    remote_issue = GitHubIssue(gh=gh,
                               number=local_issue.get('number'))
    # Validate GitHub issue against JSON schema
    remote_issue.validate(action=args.command,
                          projects=get_projects(cfg))
    # Close the ESGF issue on the Github repository
    local_issue.close(gh=gh,
                      remote_issue=remote_issue)

def retrieve_issue(issue, dsets):
    """Given a JSON file and a list of dataset IDs, this will create the issue entry.

    :param issue: Handle identifier
    :return: errata information, dset/file_id
    """
    for directory in [args.issues, args.dsets]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    if args.id:
        for n in args.id:
            # Get issue number
            number = get_number(gh, n)
            # Get corresponding GitHub issue
            remote_issue = GitHubIssue(gh=gh,
                                       number=number)
            # Validate GitHub issue against JSON schema
            remote_issue.validate(action=args.command,
                                  projects=get_projects(cfg))
            # Retrieve the corresponding GitHub issue
            remote_issue.retrieve(issue_f=open('{0}/issue-{1}.json'.format(os.path.realpath(args.issues),
                                                                           number), 'w'),
                                  dsets_f=open('{0}/dsets-{1}.list'.format(os.path.realpath(args.dsets),
                                                                           number), 'w'))
    else:
        for issue in gh.iter_issues(state='all'):
            # Get corresponding GitHub issue
            remote_issue = GitHubIssue(gh=gh,
                                       number=get_number(gh, issue.number))
            # Validate GitHub issue against JSON schema
            remote_issue.validate(action=args.command,
                                  projects=get_projects(cfg))
            # Retrieve the corresponding GitHub issue
            remote_issue.retrieve(issue_f=open('{0}/issue-{1}.json'.format(os.path.realpath(args.issues),
                                                                           issue.number), 'w'),
                                  dsets_f=open('{0}/dsets-{1}.list'.format(os.path.realpath(args.dsets),
                                                                           issue.number), 'w'))

