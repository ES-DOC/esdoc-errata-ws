#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Useful functions to use with esgissue module.

"""
import argparse
import collections
import ConfigParser
import os
import re
import string
import sys
import textwrap
import uuid
from json import dump
from json import load

import requests
from bs4 import BeautifulSoup
from github3 import GitHub
from jsonschema import validate

from errata.utils import logger



__FILL_VALUE__ = unicode('Not documented')
__JSON_SCHEMA_PATHS__ = {'create': '{0}/templates/create.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'update': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'close': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'retrieve': '{0}/templates/retrieve.json'.format(os.path.dirname(os.path.abspath(__file__)))}


class MultilineFormatter(argparse.HelpFormatter):
    """Custom formatter class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.html>`_ module.

    """
    def __init__(self, prog):
        """Instance constructor.

        """
        super(MultilineFormatter, self).__init__(prog, max_help_position=60, width=100)


    def _fill_text(self, text, width, indent):
        """Rewrites the _fill_text method to support multiline description.

        """
        text = self._whitespace_matcher.sub(' ', text).strip()
        multiline_text = ''
        paragraphs = text.split('|n|n ')
        for paragraph in paragraphs:
            lines = paragraph.split('|n ')
            for line in lines:
                formatted_line = textwrap.fill(line, width,
                                               initial_indent=indent,
                                               subsequent_indent=indent) + '\n'
                multiline_text += formatted_line
            multiline_text += '\n'
        return multiline_text


    def _split_lines(self, text, width):
        """Rewrites the _split_lines method to support multiline helps.

        """
        text = self._whitespace_matcher.sub(' ', text).strip()
        lines = text.split('|n ')
        multiline_text = []
        for line in lines:
            multiline_text.append(textwrap.fill(line, width))
        multiline_text[-1] += '\n'
        return multiline_text


class MyOrderedDict(collections.OrderedDict):
    """OrderedDict instance with prepend method to add key as first.

    """
    def prepend(self, key, value, dict_setitem=dict.__setitem__):
        """Adds a keyed value to first position within underlying dictionary.

        """
        root = self._OrderedDict__root
        first = root[1]

        if key in self:
            link = self._OrderedDict__map[key]
            link_prev, link_next, _ = link
            link_prev[1] = link_next
            link_next[0] = link_prev
            link[0] = root
            link[1] = first
            root[1] = first[0] = link
        else:
            root[1] = first[0] = self._OrderedDict__map[key] = [root, first, key]
            dict_setitem(self, key, value)


class DictDiff(object):
    """
    Returns the difference between two dictionaries as:
     * keys added,
     * keys removed,
     * changed keys,
     * unchanged keys.

    :param dict old_dict: The first/old dictionary
    :param dict old_dict: The last/new dictionary to compare with
    :returns: Lists of keys
    :rtype: *list*

    """
    def __init__(self, old_dict, new_dict):
        self.new_dict, self.old_dict = new_dict, old_dict
        self.new_keys, self.old_keys = [set(d.keys()) for d in (new_dict, old_dict)]
        self.intersect = self.new_keys.intersection(self.old_keys)

    def added(self):
        return self.new_keys.difference(self.intersect)

    def removed(self):
        return self.old_keys.difference(self.intersect)

    def changed(self):
        return set(item for item in self.intersect
                   if self.old_dict[item] != self.new_dict[item])

    def unchanged(self):
        return set(item for item in self.intersect
                   if self.old_dict[item] == self.new_dict[item])


class ListDiff(object):
    """
    Returns the difference between two lists as:
     * items added,
     * items removed.

    :param list old_list: The first/old list
    :param list new_list: The last/new list to compare with
    :returns: Lists of items
    :rtype: *list*

    """
    def __init__(self, old_list, new_list):
        self.new_list, self.old_list = set(new_list), set(old_list)
        self.intersect = self.new_list.intersection(self.old_list)

    def added(self):
        return self.new_list.difference(self.intersect)

    def removed(self):
        return self.old_list.difference(self.intersect)


def config_parse(config_dir):
    """
    Parses the configuration file if exists. Tests if required options are declared.

    :param str config_dir: The absolute or relative path of the configuration file directory
    :returns: The configuration file parser
    :rtype: *dict*
    :raises Error: If no configuration file exists
    :raises Error: If sections are missing
    :raises Error: If options are missing
    :raises Error: If the configuration file parsing fails

    """
    __CONFIG_SCHEMA__ = {'issues': ['gh_login',
                                    'gh_password',
                                    'gh_team',
                                    'gh_repo',
                                    'prefix',
                                    'url_messaging_service',
                                    'messaging_exchange',
                                    'rabbit_username',
                                    'rabbit_password']}
    if not os.path.isfile('{0}/esg.ini'.format(os.path.normpath(config_dir))):
        raise Exception('"esg.ini" file not found')
    cfg = ConfigParser.ConfigParser()
    cfg.read('{0}/esg.ini'.format(os.path.normpath(config_dir)))
    if not cfg:
        raise Exception('Configuration file parsing failed')
    for section in __CONFIG_SCHEMA__:
        if not cfg.has_section(section):
            raise Exception('No "{0}" section found in "esg.ini"'.format(section))
        for option in __CONFIG_SCHEMA__[section]:
            if not cfg.has_option(section, option):
                raise Exception('"{0}" option is missing in section "{1}" of "esg.ini"'.format(option, section))
    return cfg


def test_url(url):
    """
    Tests an url response.

    :param str url: The url to test
    :returns: True if the url exists
    :rtype: *boolean*
    :raises Error: If an HTTP request fails

    """
    try:
        r = requests.head(url)
        if r.status_code != requests.codes.ok:
            logger.log('{0}: {1}'.format(r.status_code, url))
        return r.status_code == requests.codes.ok
    except:
        logger.log_error('Result: FAILED // Bad HTTP request')
        sys.exit(1)


def test_pattern(text):
    """
    Tests a regex pattern on a string.

    :param str text: The item as a string
    :returns: True if matched
    :rtype: *boolean*

    """
    pattern = "^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+#[0-9]{8}$"
    if not re.match(re.compile(pattern), text):
        logger.log('{0} is malformed'.format(text))
        return False
    else:
        return True


def traverse(l, tree_types=(list, tuple)):
    """
    Iterates through a list of lists and extracts items

    :param list l: The list to parse
    :param tuple tree_types: Iterable types
    :returns: A list of extracted items
    :rtype: *list*

    """
    if isinstance(l, tree_types):
        for item in l:
            for child in traverse(item, tree_types):
                yield child
    else:
        yield l


def split_line(line, sep='|'):
    """
    Split a line into fields removing trailing and leading characters.

    :param str line: String line to split
    :param str sep: Separator character
    :returns:  A list of string fields

    """
    fields = map(string.strip, line.split(sep))
    return fields


__version__ = '0.1'


def get_args():
    """
    Returns parsed command-line arguments. See ``esgissue -h`` for full description.

    :returns: The corresponding ``argparse`` Namespace

    """
    __TEMPLATE_HELP__ = """Required path of the issue JSON template."""
    __DSETS_HELP__ = """Required path of the affected dataset IDs list."""
    __HELP__ = """Show this help message and exit."""
    __LOG_HELP__ = """Logfile directory. If not, standard output is used."""
    parser = argparse.ArgumentParser(
        prog='esgissue',
        description="""The publication workflow on the ESGF nodes requires to deal with errata issues.
                    The background of the version changes has to be published alongside the data: what was updated,
                    retracted or removed, and why. Consequently, the publication of a new version of a dataset has to
                    be motivated by an issue.|n|n

                    "esgissue" allows the referenced data providers to easily create, document, update, close or remove
                    a validated issue. "esgissue" relies on the GitHub API v3 to deal with private repositories.|n|n

                    The issue registration always appears prior to the publication process and should be mandatory
                    for additional version, version removal or retraction.|n|n

                    "esgissue" works with both JSON and TXT files. This allows the data provider in charge of ESGF
                    issues to manage one or several JSON templates gathering the issues locally.|n|n

                    See full documentation on http://esgissue.readthedocs.org/""",
        formatter_class=MultilineFormatter,
        add_help=False,
        epilog="""Developed by:|n
                  Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)|n
                  Bennasser, A. (UPMC/IPSL - abennasser@ipsl.jussieu.fr""")
    parser._optionals.title = "Optional arguments"
    parser._positionals.title = "Positional arguments"
    parser.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)
    parser.add_argument(
        '-V',
        action='version',
        version='%(prog)s ({0})'.format(__version__),
        help="""Program version.""")
    subparsers = parser.add_subparsers(
        title='Issue actions',
        dest='command',
        metavar='',
        help='')
    retrieve = subparsers.add_parser(
        'retrieve',
        prog='esgissue retrieve',
        description=""""esgissue retrieve" retrieves one or several issues from a defined GitHub repository. The data
                    provider submits one or several issue number he wants to retrieve and optional paths to write
                    them.|n|n

                    This action rebuilds:|n
                    - the corresponding issue template as a JSON file,|n
                    - the attached affected datasets list as a TEXT file.|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO RETRIEVE AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Retrieves ESGF issues from the GitHub repository to a JSON template. See |n
             "esgissue retrieve -h" for full help.""",
        add_help=False)
    retrieve._optionals.title = "Optional arguments"
    retrieve._positionals.title = "Positional arguments"
    retrieve.add_argument(
        '--id',
        metavar='ID',
        type=str,
        nargs='+',
        help='One or several issue number(s) or ESGF id(s) to retrieve.|n Default is to retrieve all GitHub issues.')
    retrieve.add_argument(
        '--issue',
        nargs='?',
        metavar='$PWD/issues',
        default='{0}/issues'.format(os.getcwd()),
        type=str,
        help="""Output directory for the retrieved JSON templates.""")
    retrieve.add_argument(
        '--dsets',
        nargs='?',
        metavar='$PWD/dsets',
        default='{0}/dsets'.format(os.getcwd()),
        type=str,
        help="""Output directory for the retrieved lists of affected dataset IDs.""")
    retrieve.add_argument(
        '-i',
        metavar='/esg/config/esgcet/.',
        type=str,
        default='/esg/config/esgcet/.',
        help="""Initialization/configuration directory containing "esg.ini"|n
                and "esg.<project>.ini" files. If not specified, the usual|n
                datanode directory is used.""")
    retrieve.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help=__LOG_HELP__)
    retrieve.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    retrieve.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)
    return parser.parse_args()


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


def github_connector(username, password, team, repo, cfg):
    """
    Instantiates the GitHub repository connector if granted for user.

    :param str username: The GitHub login
    :param str password: The GitHub password
    :param str team: The GitHub team to connect
    :param str repo: The GitHub repository to reach

    :returns: The GitHub repository connector and the GitHub user login
    :rtype: *tuple* of (*str*, *github3.repos.repo*)

    :raises Error: If the GitHub connection fails because of invalid inputs

    """
    gh_link = {'team': cfg.get('issues', 'gh_team'),
               'repo': cfg.get('issues', 'gh_repo').lower()}
    logger.log('Connection to the GitHub repository "{team}/{repo}"'.format(**gh_link))
    try:
        gh_user = GitHub(username, password)
        gh_repo = gh_user.repository(team, repo.lower())
        logger.log('Result: SUCCESSFUL')
        return username, gh_repo
    except:
        logger.log_error('Result: FAILED // Access denied')
        sys.exit(1)


def get_projects(config):
    """Returns project options pulled from esg.ini file.

    :param dict config: The configuration file parser

    :returns: The project options
    :rtype: *list*

    """
    project_options = split_line(config.get('DEFAULT', 'project_options'), sep='\n')

    return [option[0].upper() for option in map(lambda x: split_line(x), project_options[1:])]


def get_file_number(dir_path, extension):
    """Returns the number of files with a specific extension in a directory

    :param dir_path: directory
    :param extension: extension

    :return: number of files

    """
    number_of_files = len([name for name in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, name)) and
                          name.lower().endswith(extension)])

    return number_of_files + 1


class GitHubIssue(object):
    """
    Encapsulates the following issue context/information from GitHub and
    provides related methods to deal with:

    +--------------------+-------------+------------------------------------+
    | Attribute          | Type        | Description                        |
    +====================+=============+====================================+
    | *self*.number      | *int*       | The issue number                   |
    +--------------------+-------------+------------------------------------+
    | *self*.raw         | *dict*      | The raw GitHub issue               |
    +--------------------+-------------+------------------------------------+
    | *self*.attributes  | *dict*      | The issues attributes              |
    +--------------------+-------------+------------------------------------+
    | *self*.dsets       | *list*      | The affected datasets              |
    +--------------------+-------------+------------------------------------+
    | *self*.status      | *str*       | The issue status                   |
    +--------------------+-------------+------------------------------------+
    | *self*.url         | *str*       | The issue HTML url                 |
    +--------------------+-------------+------------------------------------+
    | *self*.assignee    | *str*       | The GitHub login of issue assignee |
    +--------------------+-------------+------------------------------------+

    The attributes keys are the same as the :func:`ESGFIssue` class.

    :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
    :param int number: The issue number

    :returns: The issue context
    :rtype: *GitHubIssue*

    """
    def __init__(self, gh, number):
        self.number = number
        self.raw = None
        self.status = None
        self.assignee = None
        self.attributes, self.dsets = self.get_template(gh)


    def get(self, key):
        """
        Returns the attribute value corresponding to the key.
        The submitted key can refer to `GitHubIssue.key` or `GitHubIssue.attributes[key]`.

        :param str key: The key
        :returns: The corresponding value
        :rtype: *str* or *list* or *dict* depending on the key

        """
        if key in self.attributes:
            return self.attributes[key]
        elif key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            raise Exception('{0} not found. Available keys are {1}'.format(key, self.attributes.keys()))


    def get_template(self, gh):
        """
        Loads an issue template from the GitHub repository.

        :param *GitHubObj* gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
        :returns: The issue attributes
        :rtype: *dict*
        :raises Error: If the GitHub issue cannot be reached

        """
        self.raw = gh.issue(self.number)
        if not self.raw:
            raise Exception('Cannot get GitHub issue number {0}'.format(self.number))
        self.status = self.raw.state
        self.assignee = self.raw.assignee.login
        return self.format()


    def format(self):
        """
        Formats a GitHub issue to an ESGFIssue template.

        :returns: The formatted issue
        :rtype: *dict*

        """
        content = self.issue_content_parser(self.raw.body)
        labels = [tuple(label.name.split(': ')) for label in self.raw.labels]
        issue = MyOrderedDict()
        # issue[unicode('status')] = self.status
        issue[unicode('institute')] = [label[1] for label in labels if 'Institute' in label][0]
        issue[unicode('number')] = self.raw.number
        issue[unicode('id')] = content['id']
        issue[unicode('title')] = self.raw.title
        issue[unicode('description')] = content['description']
        issue[unicode('project')] = [label[1] for label in labels if 'Project' in label][0]
        issue[unicode('models')] = [label[1] for label in labels if 'Model' in label]
        issue[unicode('severity')] = [label[1] for label in labels if 'Severity' in label][0]
        if content['url'] != __FILL_VALUE__:
            issue[unicode('url')] = content['url']
        if content['materials'] != __FILL_VALUE__:
            issue[unicode('materials')] = content['materials']
        issue[unicode('status')] = [label[1] for label in labels if 'State' in label][0]
        issue[unicode('created_at')] = self.raw.created_at.isoformat()
        issue[unicode('last_updated_at')] = self.raw.updated_at.isoformat()
        if self.raw.is_closed():
            issue[unicode('closed_at')] = self.raw.closed_at.isoformat()
        return issue, content['dsets']


    @staticmethod
    def issue_content_parser(content):
        """
        Parses a raw issue content from GitHub and translates it into an ESGF issue template.

        :param str content: The issue content
        :returns: The issue attributes
        :rtype: *dict*

        """
        html_content = BeautifulSoup(re.sub('[\n\t\r]', '', content), "html.parser")
        html_dict = dict()
        for elt in html_content.find_all('div'):
            output_img = []
            output_dsets = []
            for parent in elt.contents:
                if parent.name == 'img':
                    output_img.append(parent['src'])
                    html_dict[elt['id']] = output_img
                elif parent.name == 'ul':
                    for child in parent.find_all('li'):
                        output_dsets.append(child.string)
                        html_dict[elt['id']] = output_dsets
                else:
                    html_dict[elt['id']] = parent.string
        return html_dict


    def validate(self, action, projects):
        """
        Validates GitHub issue template against predefined JSON schema

        :param str action: The issue action/command
        :param list projects: The projects options from esg.ini
        :raises Error: If the template has an invalid JSON schema
        :raises Error: If the project option does not exist in esg.ini
        :raises Error: If the landing page or materials urls cannot be reached.
        :raises Error: If dataset ids are malformed

        """
        logger.log('Validation of GitHub issue {0}'.format(self.attributes['number']))

        # Load JSON schema for issue template
        with open(__JSON_SCHEMA_PATHS__[action]) as fstream:
            schema = load(fstream)

        # Validate issue attributes against JSON issue schema
        try:
            validate(self.attributes, schema)
        except:
            logger.log_error('Result: FAILED // GitHub issue {0} has an invalid JSON schema'.format(self.number))
            sys.exit(1)

        # Test if project is declared in esg.ini
        if not self.attributes['project'] in projects:
            logger.log_error('Result: FAILED // Project should be one of {0}'.format(projects))
            logger.log('Local "{0}" -> "{1}"'.format('project', self.attributes['project']))
            sys.exit(1)

        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.attributes.get, ['url', 'materials'])))
        if not all(map(test_url, urls)):
            logger.log_error('Result: FAILED // URLs cannot be reached')
            sys.exit(1)

        # Validate the datasets list against the dataset id pattern
        if not all(map(test_pattern, self.dsets)):
            logger.log_error('Result: FAILED // Dataset IDs have invalid format')
            sys.exit(1)
        logger.log('Result: SUCCESSFUL')


    def retrieve(self, issue_f, dsets_f):
        """
        Retrieves a GitHub issue and writes ESGF template into JSON file and affected datasets list into TXT file

        :param FileObj issue_f: The JSON file to write in
        :param FileObj dsets_f: The TXT file to write in

        """
        logger.log('Retrieve GitHub issue #{0} JSON template'.format(self.number))
        try:
            with issue_f as json_file:
                dump(self.attributes, json_file, indent=0)
            logger.log('Result: SUCCESSFUL')
        except:
            logger.log_error('Result: FAILED // JSON template {0} is not writable'.format(issue_f.name))
            sys.exit(1)
        logger.log('Retrieve GitHub issue #{0} affected datasets list'.format(self.number))
        try:
            with dsets_f as list_file:
                list_file.write('\n'.join(self.dsets))
            logger.log('Result: SUCCESSFUL')
        except:
            logger.log_error('Result: FAILED // Dataset list {0} is not writable'.format(dsets_f.name))
            sys.exit(1)
