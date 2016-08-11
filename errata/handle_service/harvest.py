# -*- coding: utf-8 -*-
"""
.. module:: handle_service.harvest.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Handle service harvester.

.. moduleauthor:: Atef Bennasser <abennasser@ipsl.jussieu.fr>


"""
from time import time

from b2handle.handleclient import EUDATHandleClient

from errata.handle_service.crawler import crawler_v1
from errata.handle_service.utils import get_handle_by_handle_string
from errata.utils import logger



def harvest_errata_information(input_handle_string):
    """Given a handle, this will harvest all the errata data related to that handle as well as the previous versions.

    :param input_handle_string: Handle identifier
    :return: errata information, dset/file_id
    """
    tick = time()
    logger.log("--CREATING HANDLE CLIENT--")
    handle_client = EUDATHandleClient.instantiate_for_read_access()
    logger.log("--HANDLE CLIENT CREATED--")
    logger.log("----------------------------------BEGIN ISSUE TRACKING----------------------------------")
    handle = get_handle_by_handle_string(input_handle_string, handle_client)

    # initialize the handleRegister instance
    crawler_output = crawler_v1(handle, input_handle_string, handle_client)
    # crawler_output = crawler(handle, input_handle_string, handle_client)
    list_of_uids = crawler_output[0]
    dataset_or_file_id = crawler_output[1]
    is_latest = crawler_output[2]
    has_issues = crawler_output[3]
    incomplete_retracing = crawler_output[4]
    logger.log("ELAPSED TIME TILL COMPLETION : " + str(time()-tick) + " SECONDS")
    logger.log("-----------------------------------END ISSUE TRACKING-----------------------------------")
    logger.log("LIST OF UIDS GENERATED IS...")
    logger.log(list_of_uids)

    return list_of_uids, dataset_or_file_id, is_latest, has_issues, incomplete_retracing
