import esgfpid
import logging
import datetime


# Rabbit Connection Config:
# This uses the library version before open rabbit nodes were discarded

PREFIX = '21.14100'
RABBIT_EXCHANGE = 'esgffed-exchange'


RABBIT_USER_TRUSTED = 'esgf-publisher'
RABBIT_URL_TRUSTED = 'handle-esgf-open.dkrz.de'
RABBIT_PASSWORD_TRUSTED = '975a21fe1e'
RABBIT_URLS_OPEN = []
RABBIT_USER_OPEN = 'esgf-publisher-open'
IS_TEST = False
data_node1 = 'foo'
thredds_service_path1 = 'bar'


def create_connector():

    # Information about one data node:
    trusted_node_1 = {
        'user': RABBIT_USER_TRUSTED,
        'password': RABBIT_PASSWORD_TRUSTED,
        'url': RABBIT_URL_TRUSTED,
        'priority': 1
    }
    open_node = {
        'user': RABBIT_USER_OPEN,
        'url': RABBIT_URLS_OPEN
    }

    list_cred = [trusted_node_1, open_node]

    # Initialize library for that data node:
    return esgfpid.Connector(
            messaging_service_credentials=list_cred,
            handle_prefix=PREFIX,
            messaging_service_exchange_name=RABBIT_EXCHANGE,
            data_node=data_node1,
            thredds_service_path=thredds_service_path1,
            test_publication=IS_TEST
            )


def add_errata_to_handle(dataset_id, errata_id_list, connector):
    """
    given pid connector updates given handle with proper errata uids
    :param dataset_id: dataset DRS + version separated by '#'
    :param errata_id_list: the uid of the issue
    :param connector: RabbitMQ connector
    :return: nada
    """
    drs_id = dataset_id.split('#')
    print('Adding errata to {} version {}'.format(drs_id[0], drs_id[1]))
    connector.add_errata_ids(errata_ids=errata_id_list, drs_id=drs_id[0], version_number=drs_id[1])
    print('Handle updated.')


def remove_errata_from_handle(dataset_id, errata_id_list, connector):
    """
    given pid connector removes errata_id from handle
    :param dataset_id: dataset drs + version separated by '#'
    :param errata_id_list: the uid of the issue
    :param connector: RabbitMQ connector
    :return: nada
    """
    drs_id = dataset_id.split('#')
    print('Removing errata id from {}, version {}'.format(drs_id[0], drs_id[1]))
    connector.remove_errata_ids(errata_ids=errata_id_list, drs_id=drs_id[0], version_number=drs_id[1])
    print('Handle updated.')
