# -*- coding: utf-8 -*-

"""
.. module:: errata.issue_manager.issue_manager_handler.py
   :platform: Unix
   :synopsis: Handles issue information and provides methods to deal with

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""

# TODO: Handle Service interaction with errors in case of drs_id and version number does not exists
# TODO: Handle Service interaction should consider dictionary to records hundreds of PIDs per issue
# TODO: Remove errata_id from Handle records when dataset_id are removed from input list

# Module imports
import re
import os
import sys
import logging
from uuid import uuid4
from copy import copy
from bs4 import BeautifulSoup
from utils import MyOrderedDict, DictDiff, ListDiff, test_url, test_pattern, traverse
import json
import jsonschema
from fuzzywuzzy.fuzz import token_sort_ratio
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader
from constants import __JSON_SCHEMA_PATHS__
from custom_exceptions import *
import glob
import sqlalchemy
from errata import db
from errata.constants import STATE_CLOSED
from errata.constants import STATE_OPEN
from errata.db.models import Issue, IssueDataset
from errata.utils import logger
import simplejson



# Fill value for undocumented URL or MATERIALS
__FILL_VALUE__ = unicode('Not documented')

# GitHub labels
__LABELS__ = {'Low': '#e6b8af',
              'Medium': '#dd7e6b',
              'High': '#cc4125',
              'Critical': '#a61c00',
              'New': '#00ff00',
              'On hold': '#ff9900',
              'Wontfix': '#0c343d',
              'Resolved': '#38761d',
              'project': '#a4c2f4',
              'institute': '#351c75',
              'models': '#a2c4c9'}

# Description ratio change
__RATIO__ = 20


class ESGFIssue(object):
    """
    Encapsulates the following issue context/information from local JSON template and
    provides related methods to deal with:

    +--------------------+-------------+------------------------------------+
    | Attribute          | Type        | Description                        |
    +====================+=============+====================================+
    | *self*.issue_f     | *FileObj*   | The issue template JSON file       |
    +--------------------+-------------+------------------------------------+
    | *self*.dsets_f     | *FileObj*   | The affected dataset list file     |
    +--------------------+-------------+------------------------------------+
    | *self*.attributes  | *dict*      | The issues attributes              |
    +--------------------+-------------+------------------------------------+
    | *self*.dsets       | *list*      | The affected datasets              |
    +--------------------+-------------+------------------------------------+

    The attributes keys are:
    +--------------------+-------------+------------------------------------+
    | Key                | Value type  | Description                        |
    +====================+=============+====================================+
    | *self*.number      | *int*       | The issue number                   |
    +--------------------+-------------+------------------------------------+
    | *self*.id          | *str*       | The issue ESGF id (UUID format)    |
    +--------------------+-------------+------------------------------------+
    | *self*.title       | *str*       | The issue title                    |
    +--------------------+-------------+------------------------------------+
    | *self*.description | *str*       | The issue description              |
    +--------------------+-------------+------------------------------------+
    | *self*.severity    | *str*       | The issue priority/severity level  |
    +--------------------+-------------+------------------------------------+
    | *self*.project     | *str*       | The affected project               |
    +--------------------+-------------+------------------------------------+
    | *self*.institute   | *str*       | The affected institute             |
    +--------------------+-------------+------------------------------------+
    | *self*.models      | *list*      | The affected models                |
    +--------------------+-------------+------------------------------------+
    | *self*.url         | *str*       | The landing page URL               |
    +--------------------+-------------+------------------------------------+
    | *self*.materials   | *list*      | The materials URLs                 |
    +--------------------+-------------+------------------------------------+
    | *self*.workflow    | *str*       | The issue workflow                 |
    +--------------------+-------------+------------------------------------+
    | *self*.created_at  | *str*       | The registration date (ISO format) |
    +--------------------+-------------+------------------------------------+
    | *self*.updated_at  | *str*       | The last updated date (ISO format) |
    +--------------------+-------------+------------------------------------+
    | *self*.closed_at   | *str*       | The closure date (ISO format)      |
    +--------------------+-------------+------------------------------------+

    :param FileObj issue_f: The issue template JSON file
    :param FileObj dsets_f: The affected datasets list file
    :returns: The issue context
    :rtype: *ESGFIssue*

    """
    def __init__(self, issue, dsets_f):
        print('INITIALIZING ESGFISSUE OBJECT....')
        print(type(issue))
        print(issue)
        self.attributes = issue
        print('GOT THE ISSUE...')
        self.dsets = None

    def get(self, key):
        """
        Returns the attribute value corresponding to the key.
        The submitted key can refer to `File.key` or `File.attributes[key]`.

        :param str key: The key
        :returns: The corresponding value
        :rtype: *str* or *list* or *dict* depending on the key

        """
        if key in self.attributes:
            return self.attributes[key]
        elif key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            raise Exception('{0} not found. Available keys '
                            'are {1}'.format(key, self.attributes.keys() + self.__dict__.keys()))

    @staticmethod
    def get_dsets(dsets_f):
        """
        Gets the affected datasets list from a text file.

        :param FileObj dsets_f: The affected datasets list file
        :returns: The affected datasets
        :rtype: *iter*

        """
        dsets = list()
        for dset in dsets_f:
            dsets.append(unicode(dset.strip(' \n\r\t')))
        return dsets

    def validate(self, action):
        """
        Validates ESGF issue template against predefined JSON schema

        :param str action: The issue action/command
        :raises Error: If the template has an invalid JSON schema
        :raises Error: If the project option does not exist in esg.ini
        :raises Error: If the description is already published on GitHub
        :raises Error: If the landing page or materials urls cannot be reached
        :raises Error: If dataset ids are malformed

        """
        # Load JSON schema for issue template
        print('STARTED VALIDATION PROCESS...')
        with open(__JSON_SCHEMA_PATHS__[action]) as f:
            print('LOADING FILE...')
            schema = json.load(f)
            print('FILE SUCCESSFULLY LOADED!')
        # Validate issue attributes against JSON issue schema
        try:
            print(self.attributes)
            jsonschema.validate(self.attributes, schema)
        except jsonschema.exceptions.ValidationError as e:
            print(e.message)
            raise InvalidJSONSchema
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.attributes.get, ['url', 'materials'])))
        if not all(map(test_url, urls)):
            raise UnreachableURLs
        # Validate the datasets list against the dataset id pattern
        if not all(map(test_pattern, self.dsets)):
            raise InvalidDatasetIDs
        logging.info('VALID ISSUE :: {}'.format(self.attributes['id']))

    @staticmethod
    def _get_issue(dict_instance):
        """
        Maps a dictionary decoded from a file to an issue instance.

        """
        issue = Issue()
        issue.date_created = dict_instance['created_at']
        if 'last_updated_at' in dict_instance.keys():
            issue.date_updated = dict_instance['last_updated_at']
        if 'closed_at' in dict_instance.keys():
            issue.date_closed = dict_instance['closed_at']
        issue.date_updated = dict_instance['last_updated_at']
        issue.description = dict_instance['description']
        issue.institute = dict_instance['institute'].lower()
        if 'materials' in dict_instance.keys():
            issue.materials = ",".join(dict_instance['materials'])
        issue.severity = dict_instance['severity']
        issue.state = STATE_CLOSED if issue.date_closed else STATE_OPEN
        issue.project = dict_instance['project'].lower()
        issue.title = dict_instance['title']
        issue.uid = dict_instance['id']
        if 'url' in dict_instance.keys():
            issue.url = dict_instance['url']
        issue.workflow = dict_instance['workflow']
        return issue

    @staticmethod
    def _load_issue(db_instance):
        """
        Maps an issue instance to a dictionary

        """
        issue = dict()
        issue['created_at'] = db_instance.date_created
        if db_instance.last_updated_at:
            issue['last_updated_at'] = db_instance.last_updated_at
        if db_instance.closed_at:
            issue['closed_at'] = db_instance.closed_at
        issue['description'] = db_instance.description
        issue['institute'] = db_instance.institute.upper()
        if db_instance.materials:
            issue['materials'] = [m for m in db_instance.materials.split(',')]
        issue['severity'] = db_instance.severity
        issue['project'] = db_instance.project.upper()
        issue['title'] = db_instance.title
        issue['id'] = db_instance.uid
        if db_instance.url:
            issue['url'] = db_instance.url
        issue['workflow'] = db_instance.workflow
        return issue

    def create(self):
        """
        Create an issue entry into the database.

        :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
        :param str assignee: The GitHub login of the issue assignee
        :param dict descriptions: The descriptions from all registered GitHub issues
        :raises Error: If the issue registration fails without any result

        """
        with db.session.create():
            # Test if description is not already published
            # if self.attributes['description'] in db.session.query(??):
            # # TODO: Build SQL query to get all descriptions as 'SELECT description FROM TABLE'
            #     raise InvalidDescription
            self.attributes.prepend('id', str(uuid4()))
            self.attributes.update({'workflow': unicode('new')})
            # Insert issue entry into database
            issue = self._get_issue(self.attributes)
            try:
                db.session.insert(issue)
            except sqlalchemy.exc.IntegrityError:
                logging.exception('ISSUE SKIPPED (already inserted) :: {}'.format(issue.uid))
                db.session.rollback()
            except UnicodeDecodeError:
                logging.exception('DECODING EXCEPTION')
            else:
                logging.info('ISSUE INSERTED :: {}'.format(issue.uid))
            # Insert related datasets.
            for dataset_id in self.dsets:
                dataset = IssueDataset()
                dataset.issue_id = issue.id
                dataset.dataset_id = dataset_id
                try:
                    db.session.insert(dataset)
                except sqlalchemy.exc.IntegrityError:
                    logging.error('DATASET SKIPPED (already inserted) :: {}'.format(dataset.dataset_id))
                    db.session.rollback()

    def send(self, hs):
        """
        Updates the errata id PID metadata for correspond affected datasets.

        :param ESGF_PID_connector hs: The Handle Service connector
        (as a :func:`esgfpid.ESGF_PID_connector` class instance)
        :raises Error: If the PID update fails for any other reason.

        """
        try:
            errata_id = '{0}.{1}.{2}'.format(self.attributes['project'],
                                             self.attributes['institute'],
                                             self.attributes['id'])
            for dset in self.dsets:
                drs_id, version_number = dset.split('#')
                hs.add_errata_ids(drs_id=drs_id,
                                  version_number=version_number,
                                  errata_ids=errata_id)
            logging.info('ERRATA INFORMATION SENT TO HANDLE SERVICE')
        except:
            logging.exception('FAILED TO SENT ERRATA INFORMATION TO HANDLE SERVICE')

    def update(self, gh, remote_issue):
        """
        Updates an issue on the GitHub repository.

        :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
        :param GitHubIssue remote_issue: The corresponding GitHub issue (as a :func:`GitHubIssue` class instance)
        :raises Error: If the id, title, project or dates are different
        :raises Error: If the workflow changes back to new
        :raises Error: If the issue update fails for any other reason

        """
        # with db.session.create():
        #     db_issue = self._load_issue(db.session.query())
        #     db_dsets = _load_dsets(db.session.query())
        # # Test that workflow should not change back to "New"
        # if db_issue['workflow'] != 'new' and self.attributes['workflow'] == 'new':
        #     raise InvalidStatus
        # # Test if id, title, project, institute and dates are unchanged.
        # for key in ['id', 'title', 'project', 'institute', 'created_at', 'last_updated_at']:
        #     if self.attributes[key] != db_issue[key]:
        #         raise InvalidAttribute
        # # Test the description changes by no more than 80%
        # if token_sort_ratio(self.attributes['description'], db_issue['description']) < __RATIO__:
        #     raise InvalidDescription
        # keys = DictDiff(db_issue, self.attributes)
        # dsets = ListDiff(db_dsets, self.dsets)
        # if (not keys.changed() and not keys.added() and not keys.removed() and not dsets.added() and
        #         not dsets.removed()):
        #     logging.info('Nothing to change on GitHub issue #{0}'.format(db_issue['id']))
        # else:
        #     for key in keys.changed():
        #         logging.info('CHANGE {0}'.format(key))
        #         logging.debug('Old "{0}" <- "{1}"'.format(key, db_issue[key]))
        #         logging.debug('New "{0}" -> "{1}"'.format(key, self.attributes[key]))
        #         db_issue[key] = self.attributes[key]
        #     for key in keys.added():
        #         logging.info('ADD {0}'.format(key))
        #         logging.debug('Old "{0}" <- "{1}"'.format(key, __FILL_VALUE__))
        #         logging.debug('New "{0}" -> "{1}"'.format(key, self.attributes[key]))
        #         db_issue[key] = self.attributes[key]
        #     for key in keys.removed():
        #         logging.info('REMOVE {0}'.format(key))
        #         logging.debug('Old "{0}" <- "{1}"'.format(key, db_issue[key]))
        #         logging.debug('New "{0}" -> "{1}"'.format(key, __FILL_VALUE__))
        #         del db_issue[key]
        #     # Update issue information keeping status unchanged
        #     issue = self._get_issue(db_issue)
        #     try:
        #         db.session.update(issue)
        #     except UnicodeDecodeError:
        #         logging.exception('DECODING EXCEPTION')
        #     else:
        #         logging.info('ISSUE UPDATED :: {}'.format(issue.uid))
        #
        #     for dset in dsets.removed():
        #         db.session.query(??) # TODO : 'SELECT * FROM tbl_dataset WHERE dataset_id=dset'
        #         try:
        #             db.session.insert(dataset)
        #         except sqlalchemy.exc.IntegrityError:
        #             logging.error('DATASET SKIPPED (already inserted) :: {}'.format(dataset.dataset_id))
        #             db.session.rollback()
        #
        #         logging.info('REMOVE {0}'.format(dset))
        #     for dset in dsets.added():
        #         logging.info('ADD {0}'.format(dset))
        #     db_dsets = self.dsets
        #
        #     # Insert related datasets.
        #     for dataset_id in db_dsets:
        #         dataset = IssueDataset()
        #         dataset.issue_id = issue.id
        #         dataset.dataset_id = dataset_id
        #         try:
        #             db.session.insert(dataset)
        #         except sqlalchemy.exc.IntegrityError:
        #             logging.error('DATASET SKIPPED (already inserted) :: {}'.format(dataset.dataset_id))
        #             db.session.rollback()
        pass


    def close(self, gh, remote_issue):
        """
        Close the GitHub issue

        :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
        :param GitHubIssue remote_issue: The corresponding GitHub issue (as a :func:`GitHubIssue` class instance)
        :raises Error: If the workflow is not "Wontfix" or "Resolved"
        :raises Error: If the issue status update fails

        """
        logging.info('Close GitHub issue #{0}'.format(remote_issue.number))
        # Test if all attributes are unchanged.
        for key in self.attributes:
            if self.attributes[key] != remote_issue.attributes[key]:
                logging.error('Result: FAILED // "{0}" attribute should be unchanged'.format(key))
                logging.debug('Local "{0}"  -> "{1}"'.format(key, self.attributes[key]))
                logging.debug('Remote "{0}" <- "{1}"'.format(key, remote_issue.attributes[key]))
                sys.exit(1)
        # Test if issue workflow is "Wontfix" or "Resolved"
        if not remote_issue.attributes['workflow'] in ['Wontfix', 'Resolved']:
            logging.error('Result: FAILED // Issue workflow should be "Wontfix" or "Resolved')
            logging.debug('Local "{0}"  -> "{1}"'.format('workflow', self.attributes['workflow']))
            logging.debug('Remote "{0}" <- "{1}"'.format('workflow', remote_issue.attributes['workflow']))
            sys.exit(1)
        issue = gh.issue(remote_issue.number)
        success = issue.close()
        if success:
            logging.info('Result: SUCCESSFUL')
            self.attributes.update({'last_updated_at': issue.updated_at.isoformat()})
            logging.debug('Updated at <- "{0}"'.format(self.attributes['last_updated_at']))
            self.attributes.update({'closed_at': issue.closed_at.isoformat()})
            logging.debug('Closed at <- "{0}"'.format(self.attributes['closed_at']))
            self.write()
        else:
            logging.error('Result: FAILED // "{0}" issue returned.'.format(issue))
            sys.exit(1)

    @staticmethod
    def issue_content(attributes, dsets):
        """
        Format the ESGF issue content.

        :param dict attributes: The issue attributes
        :param list dsets: The affected datasets
        :return: The html rendering
        :rtype: *str*

        """
        template = copy(attributes)
        template.update({'dsets': dsets})
        for key in ['url', 'materials']:
            if key not in attributes:
                template.update({key: None})
        engine = Engine(loader=FileLoader({'{0}/templates'.format(os.path.dirname(os.path.abspath(__file__)))}),
                        extensions=[CoreExtension()])
        html_template = engine.get_template('issue_content.html')
        return html_template.render(template)

    def write(self):
        """
        Writes an ESGF issue into JSON file.

        """
        # logging.info('Writing ESGF issue into JSON template {0}'.format(self.issue_f.name))
        # try:
        #     with open(self.issue_f.name, 'w') as json_file:
        #         dump(self.attributes, json_file, indent=0)
        #     logging.info('Result: SUCCESSFUL')
        # except:
        #     logging.exception('Result: FAILED // JSON template {0} is not writable'.format(self.issue_f.name))
        #     sys.exit(1)
        pass

class DBIssue(object):
    """
    Encapsulates the following issue context/information from database and
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
    def __init__(self, id):
        self.attributes, self.dsets = self.get_issue(id)
        self.raw = None
        self.assignee = None
        self.attributes = None
        self.dsets = None
        # self.attributes, self.dsets = self.get_template(gh)

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
        issue[unicode('number')] = self.raw.number
        issue[unicode('id')] = content['id']
        issue[unicode('title')] = self.raw.title
        issue[unicode('description')] = content['description']
        issue[unicode('project')] = [label[1] for label in labels if 'Project' in label][0]
        issue[unicode('institute')] = [label[1] for label in labels if 'Institute' in label][0]
        issue[unicode('models')] = [label[1] for label in labels if 'Model' in label]
        issue[unicode('severity')] = [label[1] for label in labels if 'Severity' in label][0]
        if content['url'] != __FILL_VALUE__:
            issue[unicode('url')] = content['url']
        if content['materials'] != __FILL_VALUE__:
            issue[unicode('materials')] = content['materials']
        issue[unicode('workflow')] = [label[1] for label in labels if 'Workflow' in label][0]
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
        logging.info('Validation of GitHub issue {0}'.format(self.attributes['number']))
        # Load JSON schema for issue template
        with open(__JSON_SCHEMA_PATHS__[action]) as f:
            schema = simplejson.load(f)
        # Validate issue attributes against JSON issue schema
        try:
            validate(self.attributes, schema)
        except:
            logging.exception('Result: FAILED // GitHub issue {0} has an invalid JSON schema'.format(self.number))
            sys.exit(1)
        # Test if project is declared in esg.ini
        if not self.attributes['project'] in projects:
            logging.error('Result: FAILED // Project should be one of {0}'.format(projects))
            logging.debug('Local "{0}" -> "{1}"'.format('project', self.attributes['project']))
            sys.exit(1)
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.attributes.get, ['url', 'materials'])))
        if not all(map(test_url, urls)):
            logging.error('Result: FAILED // URLs cannot be reached')
            sys.exit(1)
        # Validate the datasets list against the dataset id pattern
        if not all(map(test_pattern, self.dsets)):
            logging.error('Result: FAILED // Dataset IDs have invalid format')
            sys.exit(1)
        logging.info('Result: SUCCESSFUL')
        pass

    def retrieve(self, issue_f, dsets_f):
        # """
        # Retrieves a GitHub issue and writes ESGF template into JSON file and affected datasets list into TXT file
        #
        # :param FileObj issue_f: The JSON file to write in
        # :param FileObj dsets_f: The TXT file to write in
        #
        # """
        # logging.info('Retrieve GitHub issue #{0} JSON template'.format(self.number))
        # try:
        #     with issue_f as json_file:
        #         dump(self.attributes, json_file, indent=0)
        #     logging.info('Result: SUCCESSFUL')
        # except:
        #     logging.exception('Result: FAILED // JSON template {0} is not writable'.format(issue_f.name))
        #     sys.exit(1)
        # logging.info('Retrieve GitHub issue #{0} affected datasets list'.format(self.number))
        # try:
        #     with dsets_f as list_file:
        #         list_file.write('\n'.join(self.dsets))
        #     logging.info('Result: SUCCESSFUL')
        # except:
        #     logging.exception('Result: FAILED // Dataset list {0} is not writable'.format(dsets_f.name))
        #     sys.exit(1)
        pass
