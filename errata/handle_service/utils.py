import logging
import os
import uuid

import requests
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from requests.packages.urllib3.exceptions import SNIMissingWarning

from constants import *
from custom_exceptions import *
from difflib import SequenceMatcher

# Diable requests warnings.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)


# Initialize logging.
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=os.path.join("/home/abennasser", "logs/errata.log"),
                    filemode='w')


def get_handle_by_handle_string(handle_string, handle_client_instance):
    """
    Using the EUDATHandle service, this function reads the required handle using the handle_string.
    :param handle_string: String
    :param handle_client_instance: EUDATClient instance
    :return: json formatted handle
    """
    logging.debug('GETTING HANDLE FROM HANDLE SERVER WITH KEY... ' + handle_string)
    encoded_dict = handle_client_instance.retrieve_handle_record(handle_string)
    if encoded_dict is not None:
        handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
        return handle_record
    else:
        raise HandleNotFoundException


def has_successor_and_predecessors(handle):
    """
    Inspects handle for successors and predecessors
    :param handle: current handle
    :return: array of Boolean
    result[0] : predecessor
    result[1] : successor
    """
    result = [False, False]
    if SUCCESSOR in handle:
        result[1] = True
    if PREDECESSOR in handle:
        result[0] = True
    return result


def is_same_checksum(current_checksum, received_checksum):
    if current_checksum != received_checksum:
        return False
    else:
        return True


def check_presence_of_mandatory_args(args, mandatory_args):
    """
    This is needed to create the handle.
    :param args: argument required for the function but not mandatory
    :param mandatory_args: Mandatory arguments
    :return: Boolean
    """
    missing_args = []
    for name in mandatory_args:
        if name not in args.keys():
            missing_args.append(name)
    if len(missing_args) > 0:
        raise ValueError('Missing mandatory arguments: '+', '.join(missing_args))
    else:
        return True


def make_handle_from_drsid_and_versionnumber(**args):
    """
    Creates the handle string from the drs_id and the version number of the dataset.
    :param args: DRS_id, Version_number, prefix
    :return:handle string
    """
    check_presence_of_mandatory_args(args, ['drs_id', 'version_number', 'prefix'])
    suffix = make_suffix_from_drsid_and_versionnumber(drs_id=args['drs_id'], version_number=args['version_number'])
    return args['prefix']+'/'+suffix


def make_suffix_from_drsid_and_versionnumber(**args):
    """
    Needed for creating handle string.
    :param args:
    :return: handle string
    """
    check_presence_of_mandatory_args(args, ['drs_id', 'version_number'])
    hash_basis = args['drs_id']+'.v'+str(args['version_number'])
    hash_basis_utf8 = hash_basis.encode('utf-8')
    ds_uuid = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)
    return str(ds_uuid)


def get_issue_information(direction):
    """
    Retracing successors and predecessors in the tree of handles has an impact on the relevant errata information.
    This function translates this effect.
    :param direction:
    :return:
    """
    if direction == 'UP':
        return None
    elif direction == 'DOWN':
        return None


def resolve_aggregation_level(handle):
    """
    Returns whether the handle is a dataset handle or a file handle.
    Different aggregation level handles contain different entries.
    :param handle:
    :return: String containing aggregation level e.g. DATASET or FILE.
    """
    return handle['AGGREGATION_LEVEL']


def get_parent_handle(file_handle, handle_client_instance):
    """
    Using a file handle, this function returns the handle of the containing dataset
    :param file_handle: handle string of the file
    :param handle_client_instance : EUDATClient instance
    :return: file handle
    """
    return get_handle_by_handle_string(file_handle[PARENT], handle_client_instance)


def find_file_within_dataset(_dataset_handle_register, _file_handle_register, direction):
    """
    Finds specific file, designated by its filename in a dataset designated by its handle.
    :param _dataset_handle_register: handle of the dataset
    :param _file_handle_register: handle of the file
    :param direction: up or down needed for errata extraction
    :return: next_file_handle(same if it is found within dataset), errata_information(None if no change occurred)
    :except file not found in successor
    """
    # list containing the file_handle_strings
    list_of_children = _dataset_handle_register.children
    logging.debug("THE CURRENT DATASET CONTAINS " + str(len(list_of_children)) + " CHILDREN...")
    logging.debug(list_of_children)
    logging.debug("STARTING LOOP OVER CHILDREN...")
    # Test added to improve performance
    # If file handle is automatically in the list we just bypass the filename test.
    if _file_handle_register.handle not in list_of_children:
        logging.debug('FILE NOT FOUND IN CHILDREN LIST, PROCEEDING TO FILENAME TESTING...')
        for fhs in list_of_children:
            logging.debug("PROCESSING FILE " + _file_handle_register.filename + " IN COMPARISON TO " + fhs[FILE_NAME])
            logging.debug("STARTING RESEMBLANCE TEST.")
            ratio = SequenceMatcher(None, _file_handle_register.filename, fhs[FILE_NAME]).ratio()
            if _file_handle_register.filename == fhs[FILE_NAME]:
                logging.debug("FILE HAS BEEN FOUND WITHIN PREDECESSOR/SUCCESSOR COMPARING CHECKSUMS...")
                if is_same_checksum(_file_handle_register.checksum, fhs[CHECKSUM]):
                    logging.debug("SIMILAR CHECKSUMS WERE FOUND, FILE IS INTACT SO FAR...")
                    return fhs, None
                else:
                    # TODO REPLACE NONE WITH PROPER ERRATA INFO
                    logging.debug("CHECKSUM DIFFERENCE HAS BEEN DETECTED, REPLACING FILE HANDLE AND RETRIEVING ISSUE...")
                    if direction == SUCCESSOR:
                        logging.debug('FILE WAS CHANGED IN THE SUCCEDING DATASET, GETTING ISSUE FROM PREVIOUS HANDLE')
                        return fhs, _dataset_handle_register.predecessor.errata
                    elif direction == PREDECESSOR:
                        logging.debug('FILE WAS CHANGED IN THE PRECEDING DATASET, GETTING ISSUE FROM THIS HANDLE')
                        return fhs, _dataset_handle_register.errata

            elif 1 > ratio > 0.9:
                logging.info('A CONTENDER TO THAT BARES A STRONG RESEMBLANCE TO THE FILE IN HANDS HAS BEEN DETECTED...')
            else:
                pass
        logging.warn("FILE WAS NOT FOUND IN THIS PREDECESSOR/SUCCESSOR...")
        logging.warn("DEDUCING ERRATA INFORMATION ON AGGREGATION LEVEL OF FILES IS IMPOSSIBLE IN THIS CASE...")
        logging.info(_dataset_handle_register.errata)
        return _file_handle_register.handle, _dataset_handle_register.errata
    else:
        logging.debug('FILE UNCHANGED, MOVING ON...')
        return _file_handle_register.handle, None


def get_parent_handle(file_handle, handle_client_instance):
    """
    Using a file handle, this function returns the handle of the containing dataset
    :param file_handle: handle string of the file
    :param handle_client_instance : EUDATClient instance
    :return: file handle
    """
    return get_handle_by_handle_string(file_handle[PARENT], handle_client_instance)


def get_aggregation_level(handle):
    """
    returns aggregation level of handle
    :param handle:
    :return: "FILE" or "DATASET"
    """
    return handle[AGGREGATION_LEVEL]


def get_dataset_or_file_id(handle, aggregation_level):
    """
    returns the dataset/file id from handle
    :param handle: dictionary retrieved from handle service
    :param aggregation_level: Dataset or File
    :return: dataset/file id
    """
    if aggregation_level == FILE:
        return handle[FILE_NAME]
    elif aggregation_level == DATASET:
        return handle[DRS]


def get_version(handle):
    """
    returns version of dataset or file from handle
    :param handle: handle dictionary
    :return: version string
    """
    try:
        return handle[VERSION]
    except KeyError:
        logging.warn('VERSION COULD NOT BE RETRIEVED FROM HANDLE.')


def get_successor_or_predecessor(handle, key, handle_client_instance):
    """
    With direction, this gets the respective successor or predecessor
    :param handle:
    :param key:
    :param handle_client_instance:
    :return: previous/next handle
    :except Handle not found in handle-server
    """
    try:
        previous_or_next_handle = get_handle_by_handle_string(handle[key], handle_client_instance)
        # TODO save issue information
        # get_issue_information(key)
        logging.info('FOUND HANDLE ' + handle['URL'])
        return previous_or_next_handle
    except HandleNotFoundException:
        raise HandleNotFoundException


def list_children_filenames(_dataset_handle, handle_client_instance):
    """
    lists children filenames from dataset
    :param _dataset_handle: dataset handle
    :param handle_client_instance: EUDATClient instance
    :return: list of children contained in dataset
    """
    result = []
    for child in _dataset_handle[CHILDREN].split(';'):
        child_handle = get_handle_by_handle_string(child, handle_client_instance)
        result.append(child_handle[FILE_NAME])
    return result


def list_children_handles(_dataset_handle, handle_client_instance):
    """
    lists children from dataset
    :param _dataset_handle: dataset handle
    :param handle_client_instance: EUDATClient instance
    :return: list of child handle registers contained in dataset
    """
    list_of_children = []
    for child in _dataset_handle[CHILDREN].split(';'):
        child_handle = get_handle_by_handle_string(child, handle_client_instance)
        list_of_children.append(child_handle)
    return list_of_children


def get_issue_id(handle):
    """
    gets the uid for the issue of the handle
    :param handle:
    :return: uid
    """
    try:
        return handle['ERRATA_IDS']
    except KeyError:
        issue_list = ["11221244-2194-4c1f-bdea-4887036a9e63", "9de57705-48b8-4343-8bcd-22dad2c28c9a"
                      , "979e3ad5-9123-483c-89e9-c2de2372d0a8", "4d4c9942-f3a4-4538-891c-069007ed37f1"
                      , "27897958-f462-43d3-8c19-309cd6a43ce3"
                      , "96eba87b-2f6d-4eea-a474-3f5c9dff6675"]

        return random.choice(issue_list)


# def crawler(input_handle, input_handle_string, handle_client_instance):
#     """
#     Crawls up the tree on a dataset aggregation level. Can also manage on file level.
#     :param input_handle: Dataset or file Handle
#     :param handle_client_instance: EUDATClient instance
#     :param input_handle_string: handle string to be searched
#     :return: list of couples [(dataset_handler/file_handler, issue_identifier)], initial dset/file_id
#     """
#     # initializing return list
#     list_of_uids = dict()
#     # resolving whether the user input is on a file level or a dataset level.
#     aggregation_level = get_aggregation_level(input_handle)
#     # initial id will serve for web service return readability
#     initial_id = get_dataset_or_file_id(input_handle, aggregation_level)
#     # order_index is used at every loop to maintain order of successor and predecessors
#     order_index = 0
#     logging.debug('THE HANDLE PROVIDED IS OF AN AGGREGATION LEVEL ' + aggregation_level)
#     # initializing handles according to aggregation level.
#     # Please note this is for code readability purposes only.
#     if aggregation_level == FILE:
#             initial_file_handle = input_handle
#             logging.debug("GETTING PARENT HANDLE...")
#             initial_handle = get_parent_handle(input_handle, handle_client_instance)
#             logging.debug("PARENT HANDLE SUCCESSFULLY FOUND.")
#             # replacing file_handle by dataset_handle for looping purposes
#             _dataset_handle = initial_handle
#             _file_handle = input_handle
#
#     elif aggregation_level == DATASET:
#             initial_handle = input_handle
#             _dataset_handle = input_handle
#     # Added current dataset errata return information
#     list_of_uids[_dataset_handle[DRS]] = [get_issue_id(_dataset_handle), order_index]
#
#     # lineage variable contains information whether the crawler needs to go up or down the tree.
#     # lineage may indicate that the crawler needs to go both up and down, in that case, up will be treated first.
#     # The treatment will go in its entirety in one direction before assessing the other one.
#
#     lineage = has_successor_and_predecessors(_dataset_handle)
#     logging.debug("LINEAGE TEST YIELDED ")
#     logging.debug(lineage)
#     if lineage[0]:
#         logging.debug('STARTING UPWARDS CRAWLER...')
#         next_lineage = lineage
#         # if the aggregation level is file, we got up to the dataset level.
#         while _dataset_handle is not None and next_lineage[0]:
#             try:
#                 logging.debug("GETTING PREDECESSOR...")
#                 _dataset_handle = get_successor_or_predecessor(_dataset_handle, PREDECESSOR, handle_client_instance)
#                 next_lineage = has_successor_and_predecessors(_dataset_handle)
#                 logging.debug("PREDECESSOR FOUND WITH THE FOLLOWING LINEAGE ")
#                 logging.debug(next_lineage)
#                 order_index -= 1
#                 list_of_uids[_dataset_handle[DRS]] = [get_issue_id(_dataset_handle), order_index]
#                 if aggregation_level == FILE:
#                     try:
#                         find_file_within_dataset(_dataset_handle, _file_handle, input_handle_string,
#                                                  handle_client_instance)
#                     except FileNotFoundInSuccessor:
#                         logging.debug("FILE SEEMS TO HAVE BEEN CREATED IN THIS DATASET...")
#             except HandleNotFoundException:
#                 logging.debug('A LOOKUP FOR A PREVIOUS HANDLE HAS FAILED FOR THE HANDLE ' +
#                               _dataset_handle[PREDECESSOR])
#                 break
#         logging.debug('EXITING UPWARDS CRAWLER...')
#
#     # Reinitializing handle in case it got modified in the process of finding a predecessor
#     logging.debug('UPWARDS LOOP HAS BEEN COMPLETED, HANDLE IS NOW RESTORED TO START LEVEL...')
#     _dataset_handle = initial_handle
#     order_index = 0
#
#     if lineage[1]:
#         logging.debug('STARTING DOWNWARDS CRAWLER...')
#         next_lineage = lineage
#         while _dataset_handle is not None and next_lineage[1]:
#             try:
#                 logging.debug("FINDING SUCCESSOR...")
#                 _dataset_handle = get_successor_or_predecessor(_dataset_handle, SUCCESSOR, handle_client_instance)
#                 next_lineage = has_successor_and_predecessors(_dataset_handle)
#                 logging.debug("SUCCESSOR FOUND WITH THE FOLLOWING LINEAGE")
#                 logging.debug(next_lineage)
#                 order_index += 1
#                 list_of_uids[_dataset_handle[DRS]] = [get_issue_id(_dataset_handle), order_index]
#                 if aggregation_level == FILE:
#                     try:
#                         find_file_within_dataset(_dataset_handle, _file_handle, input_handle_string,
#                                                  handle_client_instance)
#                     except FileNotFoundInSuccessor:
#                         logging.warn("COULD NOT DEDUCE FURTHER ERRATA HISTORY SINCE FILE "
#                                      "DISAPPEARED IN SUCCESSOR...")
#                         # in case one failure of finding files is disregarded remove the break.
#                         break
#             except HandleNotFoundException:
#                 logging.debug('A LOOKUP FOR A SUCCESSOR HANDLE HAS FAILED' + _dataset_handle[SUCCESSOR])
#                 break
#         logging.debug('EXITING DOWNWARDS CRAWLER...')
#
#     return list_of_uids, initial_id


