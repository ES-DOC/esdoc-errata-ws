from time import time
from b2handle.handleclient import EUDATHandleClient
import logging
from utils import crawler, get_handle_by_handle_string


def harvest_errata_information(input_handle_string):
    """
    Given a handle, this will harvest all the errata data related to that handle as well as the previous versions.
    :param input_handle_string: Handle identifier
    :return: errata information
    """
    tick = time()
    logging.info("--CREATING HANDLE CLIENT--")
    handle_client = EUDATHandleClient.instantiate_for_read_access()
    logging.info("--HANDLE CLIENT CREATED--")
    logging.info("----------------------------------BEGIN ISSUE TRACKING----------------------------------")
    handle = get_handle_by_handle_string(input_handle_string, handle_client)
    list_of_uids = crawler(handle, input_handle_string, handle_client)
    logging.info("ELAPSED TIME TILL COMPLETION : " + str(time()-tick) + " SECONDS")
    logging.info("-----------------------------------END ISSUE TRACKING-----------------------------------")
    list_of_uids = ["11111111-1111-1111-1111-1111111111", "11221244-2194-4c1f-bdea-4887036a9e63"]
    return list_of_uids
