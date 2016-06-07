import logging
from time import time

from b2handle.handleclient import EUDATHandleClient

from utils import crawler
from utils import get_handle_by_handle_string


def harvest_errata_information(input_handle_string):
    """Given a handle, this will harvest all the errata data related to that handle as well as the previous versions.

    :param input_handle_string: Handle identifier
    :return: errata information, dset/file_id
    """
    tick = time()
    logging.info("--CREATING HANDLE CLIENT--")
    handle_client = EUDATHandleClient.instantiate_for_read_access()
    logging.info("--HANDLE CLIENT CREATED--")
    logging.info("----------------------------------BEGIN ISSUE TRACKING----------------------------------")
    handle = get_handle_by_handle_string(input_handle_string, handle_client)
    print handle
    crawler_output = crawler(handle, input_handle_string, handle_client)
    list_of_uids = crawler_output[0]
    dataset_or_file_id = crawler_output[1]
    logging.info("ELAPSED TIME TILL COMPLETION : " + str(time()-tick) + " SECONDS")
    logging.info("-----------------------------------END ISSUE TRACKING-----------------------------------")
    logging.info("LIST OF UIDS GENERATED IS...")
    logging.info(list_of_uids)
    return list_of_uids, dataset_or_file_id

