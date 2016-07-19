from constants import *
from utils import get_handle_by_handle_string, list_children_handles, make_handle_from_drsid_and_versionnumber
import sys

import logging, os
from custom_exceptions import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=os.path.join(os.getenv("ERRATA_HOME"), "logs/errata.log"),
                    filemode='w')


class GenericHandleRegister(object):
    """
    entity parsing the handle registry response.
    """
    def __init__(self):
        self.checksum = None
        self.url = None
        self.aggregation = None


class DatasetHandleRegister(GenericHandleRegister):
    def __init__(self, handle, handle_client_instance, **kwargs):
        self.url = handle[URL]
        self.aggregation = handle[AGGREGATION_LEVEL]
        self.lineage = [False, False]
        if 'successor' not in kwargs:
            try:
                logging.debug('RETRIEVING SUCCESSOR FOR DATASET HANDLE REGISTER...')
                try:
                    self.successor = get_handle_by_handle_string(handle[SUCCESSOR], handle_client_instance)
                    self.latest = False
                    self.lineage[1] = True
                except HandleNotFoundException:
                    logging.WARN('SUCCESSOR HANDLE COULD NOT BE FETCHED FROM PID SERVER...')
                logging.debug('SUCCESSOR SUCCESSFULLY RETRIEVED...')
            except KeyError:
                self.latest = True
        else:
            logging.debug('RETRIEVING SUCCESSOR FROM PREVIOUS LOOP...')
            self.successor = kwargs['successor']
            self.latest = False
            self.lineage[1] = True
            logging.debug('SUCCESSOR FROM PREVIOUS LOOP SUCCESSFULLY RETRIEVED...')
        if 'predecessor' not in kwargs:
            try:
                try:
                    logging.debug('RETRIEVING PREDECESSOR FOR DATASET HANDLE REGISTER...')
                    self.predecessor = get_handle_by_handle_string(handle[PREDECESSOR], handle_client_instance)
                    self.lineage[0] = True
                except HandleNotFoundException:
                    logging.warn('HANDLE COULD NOT BE FETCHED FROM HANDLE SERVER')
                logging.debug('PREDECESSOR SUCCESSFULLY RETRIEVED...')
            except KeyError:
                self.first = True
        else:
            logging.debug('RETRIEVING PREDECESSOR FROM PREVIOUS LOOP...')
            self.predecessor = kwargs['predecessor']
            self.lineage[0] = True
            logging.debug('PREDECESSOR FROM PREVIOUS LOOP HAS BEEN RETRIEVED...')
        logging.debug('LISTING CHILDREN...')
        self.children = list_children_handles(handle, handle_client_instance)
        logging.debug('CHILDREN LIST ESTABLISHED...')
        self.id = handle[DRS]
        self.version = handle[VERSION]
        self.errata = None
        try:
            self.errata = handle[ERRATA_IDS]
            self.has_issue = True
        except KeyError:
            self.has_issue = False
        self.handle_string = make_handle_from_drsid_and_versionnumber(prefix=PORT, drs_id=self.id, version_number=self.version)
        self.handle = handle

    def get_successor(self, handle_client_instance):
        """
        :param handle_client_instance
        :return successor handle
        """
        return get_handle_by_handle_string(self.successor, handle_client_instance)

    def get_predecessor(self, handle_client_instance):
        """
        :param handle_client_instance
        :return predecessor handle
        """
        return get_handle_by_handle_string(self.predecessor, handle_client_instance)


class FileHandleRegister(GenericHandleRegister):
    def __init__(self, handle, handle_client_instance, parent_handle):
        """
        Needs handle client instance to get parent
        """
        self.checksum = handle[CHECKSUM]
        self.url = handle[URL]
        self.aggregation = handle[AGGREGATION_LEVEL]
        self.filename = handle[FILE_NAME]
        self.parent_handle_string = handle[PARENT]
        # logging.DEBUG('SETTING THE PARENT HANDLE REGISTER TO FILE REGISTER, THIS WILL FLOOD THE LOG WITH SUCCESSOR'
        #               'AND PREDECESSOR FETCHING PROCESS...')
        if parent_handle is not None:
            self.parent_handle = parent_handle
        else:
            self.parent_handle = DatasetHandleRegister(self.get_parent_handle(handle_client_instance), handle_client_instance)
        self.id = handle[FILE_NAME]
        self.handle = handle

    def get_parent_handle(self, handle_client_instance):
        """
        :param handle_client_instance: instance of the handle client
        :return: parent handle
        """
        return get_handle_by_handle_string(self.parent_handle_string, handle_client_instance)





