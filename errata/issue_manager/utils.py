#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Useful functions to use with esgissue module.

"""
import ConfigParser
import os
import re
import string
import sys
import textwrap
from argparse import HelpFormatter
from collections import OrderedDict

import requests

from errata.utils import logger



class MultilineFormatter(HelpFormatter):
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
    except:
        logger.log_error('Result: FAILED // Bad HTTP request')
        sys.exit(1)
    else:
        if r.status_code != requests.codes.ok:
            logger.log('{0}: {1}'.format(r.status_code, url))
        return r.status_code == requests.codes.ok


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
    return [string.strip(i) for i in line.split(sep)]
