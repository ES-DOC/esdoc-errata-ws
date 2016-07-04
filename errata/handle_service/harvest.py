import logging
from time import time

from b2handle.handleclient import EUDATHandleClient

from crawler import crawler_v1
# from utils import crawler, crawler_v1
from utils import get_handle_by_handle_string
# from entities import *


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

    # initialize the handleRegister instance
    crawler_output = crawler_v1(handle, input_handle_string, handle_client)
    # crawler_output = crawler(handle, input_handle_string, handle_client)
    list_of_uids = crawler_output[0]
    dataset_or_file_id = crawler_output[1]
    is_latest = crawler_output[2]
    has_issues = crawler_output[3]
    incomplete_retracing = crawler_output[4]
    logging.info("ELAPSED TIME TILL COMPLETION : " + str(time()-tick) + " SECONDS")
    logging.info("-----------------------------------END ISSUE TRACKING-----------------------------------")
    logging.info("LIST OF UIDS GENERATED IS...")
    logging.info(list_of_uids)
    return list_of_uids, dataset_or_file_id, is_latest, has_issues, incomplete_retracing

# handle_string = "21.14100/atef_34416145-1309-3984-aee7-a77cdd571862"

# handle_string = "21.14100/atef_aa15a3b0-90b3-356c-b414-4529e3ac286d"
# handle_string = "21.14100/atef_2f8d3b18-bc04-3481-b28d-93c2a7b4631a"
# handle_string = "21.14100/atef_aa15a3b0-90b3-356c-b414-4529e3ac286d"
# handle_string = "21.14100/d9053480-0e0d-11e6-a148-3e1d05defe78"
# handle_string = "21.14100/37043d8e-ac5e-3843-a019-c03017cc68aa"
# handle_string = "21.14100/atef_39715308-20d2-3cc0-b893-ac364368975a"
# DATASET A
handle_string_A = '21.14100/aae01ba2-8436-378d-84ed-5a06b9fbee46'
# DATASET B
handle_string_B = '21.14100/37043d8e-ac5e-3843-a019-c03017cc68aa'
# Dataset C
handle_string_C = '21.14100/e0560a9d-2227-3175-b943-fc26c427a923'

# Dataset D
handle_string_D = '21.14100/bc3d4e81-bfbd-3a3f-a99f-4a2ec64b5962'
#
# result = harvest_errata_information(handle_string_A)
# print(result[0])
# for k, v in result[0].iteritems():
#     print type(v)
    # print('key '+ str(k))
    # print('values :')
    # print('errata: ' + str(v[0]))
    # print('id: ' + v[1])
    # print('version: ' + v[2])
    # print('order: ' + str(v[3]))
# # harvest_errata_information(handle_string_B)
# # harvest_errata_information(handle_string_C)
#
# file_handle = '21.14100/d9053480-0e0d-11e6-a148-3e1d05defe78'
# harvest_errata_information(file_handle)
