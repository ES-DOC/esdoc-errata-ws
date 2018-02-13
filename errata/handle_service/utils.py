# -*- coding: utf-8 -*-
"""
.. module:: handle_service.harvest.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Handle service utility functions.

.. moduleauthor:: Atef Bennasser <abennasser@ipsl.jussieu.fr>


"""
import random
import uuid
from difflib import SequenceMatcher

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from requests.packages.urllib3.exceptions import SNIMissingWarning

from errata.handle_service.constants import *
from errata.handle_service import constants
from errata.handle_service import exceptions
from errata.utils import logger
from errata.utils import config


# Disable requests warnings.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)


def get_handle_by_handle_string(handle_string, handle_client_instance):
    """Using the EUDATHandle service, this function reads the required handle using the handle_string.

    :param handle_string: String
    :param handle_client_instance: EUDATClient instance

    :returns: json formatted handle
    :rtype: str

    """
    logger.log('GETTING HANDLE FROM HANDLE SERVER WITH KEY... ' + handle_string)
    encoded_dict = handle_client_instance.retrieve_handle_record(handle_string)
    if encoded_dict is not None:
        handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
        return handle_record
    else:
        raise exceptions.HandleNotFoundError


def has_successor_and_predecessors(handle):
    """Inspects handle for successors and predecessors.

    :param handle: current handle

    :returns: 2 member boolean array: [0] = predecessor, [1] = successor.
    :rtype: list

    """
    result = [False, False]
    if constants.SUCCESSOR in handle:
        result[1] = True
    if constants.PREDECESSOR in handle:
        result[0] = True
    return result


def is_same_checksum(current_checksum, received_checksum):
    """
    Compares checksums
    :param current_checksum:
    :param received_checksum:
    :return: Boolean
    """
    if current_checksum != received_checksum:
        return False
    else:
        return True


def check_presence_of_mandatory_args(args, mandatory_args):
    """This is needed to create the handle.

    :param args: argument required for the function but not mandatory
    :param mandatory_args: Mandatory arguments

    :returns: True if mandatory arguments are present otherwise False.
    :rtype: Boolean

    """
    missing_args = set(mandatory_args).difference(set(args.keys()))
    if missing_args:
        raise ValueError('Missing mandatory arguments: '+', '.join(missing_args))


def make_handle_from_drsid_and_versionnumber(**args):
    """Creates the handle string from the drs_id and the version number of the dataset.

    :param args: DRS_id, Version_number, prefix

    :returns: Handle string.
    :rtype: str

    """
    check_presence_of_mandatory_args(args, ['drs_id', 'version_number', 'prefix'])
    suffix = make_suffix_from_drsid_and_versionnumber(drs_id=args['drs_id'], version_number=args['version_number'])

    return args['prefix']+'/'+suffix


def make_suffix_from_drsid_and_versionnumber(**args):
    """Needed for creating handle string.

    :param args:

    :returns: Handle string.
    :rtype: str

    """
    check_presence_of_mandatory_args(args, ['drs_id', 'version_number'])
    hash_basis = args['drs_id']+'.v'+str(args['version_number'])
    hash_basis_utf8 = hash_basis.encode('utf-8')
    ds_uuid = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)

    return str(ds_uuid)


def get_issue_information(direction):
    """Retracing successors and predecessors in the tree of handles has an impact on the relevant errata information.  This function translates this effect.

    :param direction:

    :returns:
    :rtype:

    """
    if direction == 'UP':
        return None
    elif direction == 'DOWN':
        return None


def find_file_in_dataset(dataset_record, file_record):
    """
    Finds specific file, designated by its filename in a dataset designated by its handle.
    :param dataset_record: dataset record
    :param file_record: file record
    :returns: next_file_handle(same if it is found within dataset), errata_information(None if no change occurred)
    :except file not found in successor
    """
    for child in dataset_record.children:
        if file_record.filename == child[FILE_NAME]:
            logger.log('File found by file name in dataset.')
            return child
        elif file_record.checksum == child[CHECKSUM]:
            logger.log('File found by checksum in dataset.')
            return child
        # elif SequenceMatcher(None, file_record.filename, child[FILE_NAME]).ratio() > 0.95:
        #     logger.log('Found a really similar file, {} and {}'.format(file_record.filename, child[FILE_NAME]))
        #     return child
    raise exceptions.FileNotFoundInHandle


def get_aggregation_level(handle):
    """Returns aggregation level of handle.

    :param dict handle: Handle being processed.

    :returns: Handle aggregation level (FILE | DATASET).
    :rtype: str

    """
    return handle[constants.AGGREGATION_LEVEL]


def get_dataset_or_file_id(handle, aggregation_level):
    """Returns the dataset/file id from handle

    :param handle: dictionary retrieved from handle service
    :param aggregation_level: Dataset or File

    :returns: dataset/file id
    :rtype: str

    """
    if aggregation_level == constants.FILE:
        return handle[constants.FILE_NAME]
    elif aggregation_level == constants.DATASET:
        return handle[constants.DRS]


def get_version(handle):
    """Returns version of dataset or file from handle.

    :param handle: handle dictionary

    :returns: Dataset/file version.
    :rtype: str

    """
    try:
        return handle[constants.VERSION]
    except KeyError:
        logger.log_warning('VERSION COULD NOT BE RETRIEVED FROM HANDLE.')


def get_successor_or_predecessor(handle, key, handle_client_instance):
    """With direction, this gets the respective successor or predecessor.

    :param handle:
    :param key:
    :param handle_client_instance:

    :returns: previous/next handle

    """
    previous_or_next_handle = get_handle_by_handle_string(handle[key], handle_client_instance)
    # TODO save issue information
    # get_issue_information(key)
    logger.log('FOUND HANDLE ' + handle['URL'])

    return previous_or_next_handle


def list_children_filenames(dataset_handle, handle_client_instance):
    """Lists children filenames from dataset.
    :param dataset_handle: dataset handle
    :param handle_client_instance: EUDATClient instance
    :returns: list of children contained in dataset
    :rtype: list

    """
    result = []
    # the replace has been added to remove possible prefix in handle strings retrieved from the handle server.
    for child in map(lambda x: x.replace(constants.HDL_PREFIX, ''), dataset_handle[constants.CHILDREN].split(';')):
        child_handle = get_handle_by_handle_string(child, handle_client_instance)
        result.append(child_handle[constants.FILE_NAME])
    return result


def get_issue_id(handle):
    """Gets the uid for the issue of the handle.

    :param handle: A handle being resolved to an identifier.

    :returns: uid
    :rtype: str

    """
    try:
        return handle[constants.ERRATA_IDS]
    except KeyError:
        logger.log_pid('No errata entry found for pid: {}'.format(handle))
        return None


def resolve_input(input_string):
    """
    resolves input for simple pid endpoint
    :param input_string: string
    :return: pid
    """
    if 'hdl:' in input_string:
        input_string = input_string.replace('hdl:', '')

    if config.pid.prefix in input_string:
        return input_string

    else:

        drs_id = []
        if '.v' in input_string:
            drs_id = input_string.split('.v')
        elif '#' in input_string:
            drs_id = input_string.split('#')

        if len(drs_id) > 1:
            return config.pid.prefix + '/' + make_suffix_from_drsid_and_versionnumber(drs_id=drs_id[0],
                                                                                      version_number=drs_id[1])
        else:
            logger.log_pid('UNRECOGNIZED PID OR DATASET ID.')


# def resolve_prefix(input_string):
#     """
#     This method needs to find the proper prefix per project.
#     :param input_string: /!\ could be a ready made handle string
#     :return: prefix
#     """
#     if "hdl:" in input_string:
#         pass
#     elif input_string.split('/')[0] in config.pid.prefix_list.__dict__.values():
#         pass
#     # case the input string is a dataset id
#     else:
#         if input_string.split('.')[0] in config.pid.prefix_list.__dict__.keys():
#             return config.pid.prefix_list.__dict__[input_string.split('.')[0]]
#         else:
#             logger.log_pid('UNRECOGNIZED PID OR DATASET ID: {}'.format(input_string))
