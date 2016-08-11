# -*- coding: utf-8 -*-
"""
.. module:: handle_service.entities.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Handle service handle registry response parsers.

.. moduleauthor:: Atef Bennasser <abennasser@ipsl.jussieu.fr>


"""
from errata.handle_service.constants import *
from errata.handle_service.exceptions import *
from errata.handle_service.utils import get_handle_by_handle_string
from errata.handle_service.utils import list_children_handles
from errata.handle_service.utils import make_handle_from_drsid_and_versionnumber
from errata.utils import logger



class GenericHandleRegister(object):
    """Entity parsing the handle registry response.

    """
    def __init__(self):
        """Instance constructor.

        """
        self.checksum = None
        self.url = None
        self.aggregation = None


class DatasetHandleRegister(GenericHandleRegister):
    """TODO - descirbe class.

    """
    def __init__(self, handle, handle_client_instance, **kwargs):
        """Instance constructor.

        """
        self.url = handle[URL]
        self.aggregation = handle[AGGREGATION_LEVEL]
        self.lineage = [False, False]
        if 'successor' not in kwargs:
            try:
                logger.log('RETRIEVING SUCCESSOR FOR DATASET HANDLE REGISTER...')
                try:
                    self.successor = get_handle_by_handle_string(handle[SUCCESSOR], handle_client_instance)
                    self.latest = False
                    self.lineage[1] = True
                except HandleNotFoundError:
                    logger.log_warning('SUCCESSOR HANDLE COULD NOT BE FETCHED FROM PID SERVER...')
                logger.log('SUCCESSOR SUCCESSFULLY RETRIEVED...')
            except KeyError:
                self.latest = True
        else:
            logger.log('RETRIEVING SUCCESSOR FROM PREVIOUS LOOP...')
            self.successor = kwargs['successor']
            self.latest = False
            self.lineage[1] = True
            logger.log('SUCCESSOR FROM PREVIOUS LOOP SUCCESSFULLY RETRIEVED...')
        if 'predecessor' not in kwargs:
            try:
                try:
                    logger.log('RETRIEVING PREDECESSOR FOR DATASET HANDLE REGISTER...')
                    self.predecessor = get_handle_by_handle_string(handle[PREDECESSOR], handle_client_instance)
                    self.lineage[0] = True
                except HandleNotFoundError:
                    logger.log_warning('HANDLE COULD NOT BE FETCHED FROM HANDLE SERVER')
                logger.log('PREDECESSOR SUCCESSFULLY RETRIEVED...')
            except KeyError:
                self.first = True
        else:
            logger.log('RETRIEVING PREDECESSOR FROM PREVIOUS LOOP...')
            self.predecessor = kwargs['predecessor']
            self.lineage[0] = True
            logger.log('PREDECESSOR FROM PREVIOUS LOOP HAS BEEN RETRIEVED...')
        logger.log('LISTING CHILDREN...')
        self.children = list_children_handles(handle, handle_client_instance)
        logger.log('CHILDREN LIST ESTABLISHED...')
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
    """TODO - descirbe class.

    """
    def __init__(self, handle, handle_client_instance, parent_handle):
        """Instance constructor.

        """
        self.checksum = handle[CHECKSUM]
        self.url = handle[URL]
        self.aggregation = handle[AGGREGATION_LEVEL]
        self.filename = handle[FILE_NAME]
        self.parent_handle_string = handle[PARENT]
        # logger.log('SETTING THE PARENT HANDLE REGISTER TO FILE REGISTER, THIS WILL FLOOD THE LOG WITH SUCCESSOR'
        #               'AND PREDECESSOR FETCHING PROCESS...')
        if parent_handle is not None:
            self.parent_handle = parent_handle
        else:
            self.parent_handle = DatasetHandleRegister(self.get_parent_handle(handle_client_instance), handle_client_instance)
        self.id = handle[FILE_NAME]
        self.handle = handle


    def get_parent_handle(self, handle_client_instance):
        """Returns a handles parent.

        :param handle_client_instance: instance of the handle client
        :returns: parent handle

        """
        return get_handle_by_handle_string(self.parent_handle_string, handle_client_instance)
