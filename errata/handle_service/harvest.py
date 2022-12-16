from time import time

from b2handle.handleclient import EUDATHandleClient

from errata.handle_service.crawler import crawler
from errata.handle_service.constants import ERRATA_IDS, DRS, VERSION
from errata.handle_service.utils import get_handle_by_handle_string
from errata.utils import logger


def harvest_errata_information(input_handle_string):
    """Given a handle, this will harvest all the errata data related to that handle as well as the previous versions.

    :param input_handle_string: Handle identifier
    :return: errata information, dset/file_id
    """
    tick = time()
    logger.log_pid("--CREATING HANDLE CLIENT--")
    handle_client = EUDATHandleClient.instantiate_for_read_access()
    logger.log_pid("--HANDLE CLIENT CREATED--")
    logger.log_pid("----------------------------------BEGIN ISSUE TRACKING----------------------------------")
    handle = get_handle_by_handle_string(input_handle_string, handle_client)
    list_of_uids, incomplete_search = crawler(handle, handle_client)
    logger.log_pid("ELAPSED TIME TILL COMPLETION : " + str(time()-tick) + " SECONDS")
    logger.log_pid("-----------------------------------END ISSUE TRACKING-----------------------------------")
    logger.log_pid("LIST OF UIDS GENERATED IS...")
    logger.log_pid(list_of_uids)
    return list_of_uids, incomplete_search


def harvest_simple_errata(input_handle_string):
    """
    A simplified version of the harvest original implementation.
    :param input_handle_string: pid handle string
    :return: errata_id list, empty if no errata is found.
    """
    output = []
    logger.log_pid("--CREATING HANDLE CLIENT--")
    handle_client = EUDATHandleClient.instantiate_for_read_access()
    logger.log_pid("--SUCCESSFULLY CREATED CLIENT--")
    logger.log_pid("--RETRIEVING HANDLE FROM PID SERVER--")
    handle = get_handle_by_handle_string(input_handle_string, handle_client)
    if handle is not None:
        if ERRATA_IDS in handle.keys():
            output = str(handle[ERRATA_IDS].split(";"))
        drs_id = handle[DRS]
        version = handle[VERSION]
    else:
        logger.log_pid("--HANDLE NOT FOUND IN PID SERVER--")
    return input_handle_string, drs_id, version, output, len(output) >= 1, len(drs_id) > 1

# Dataset A
# harvest_errata_information('21.14100/aae01ba2-8436-378d-84ed-5a06b9fbee46')
# Dataset B:
# harvest_errata_information('21.14100/37043d8e-ac5e-3843-a019-c03017cc68aa')
# Dataset C:
# harvest_errata_information('21.14100/e0560a9d-2227-3175-b943-fc26c427a923')
# Dataset D:
# harvest_errata_information('21.14100/bc3d4e81-bfbd-3a3f-a99f-4a2ec64b5962')
# temperature file
# harvest_errata_information('21.14100/d9053480-0e0d-11e6-a148-3e1d05defe78')
# rainfall file
# harvest_errata_information('21.14100/28ju73be-0e10-11e6-a148-a7751ce7ec0c')
# rainfall_1 file
# harvest_errata_information('21.14100/4ba213fc-f688-3d58-bd96-d984bb00f1d5')
# print(harvest_simple_errata('21.14100/4ba213fc-f688-3d58-bd96-d984bb00f1d5'))