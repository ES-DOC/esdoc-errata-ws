import esgfpid
import logging
import ConfigParser
from config import _get_config_fpath


# Rabbit Connection Config:
# This uses the library version before open rabbit nodes were discarded

# PREFIX = '21.14100'
# RABBIT_EXCHANGE = 'esgffed-exchange'
#
#
# RABBIT_USER_TRUSTED = 'esgf-publisher'
# RABBIT_URL_TRUSTED = 'handle-esgf-open.dkrz.de'
# RABBIT_PASSWORD_TRUSTED = '975a21fe1e'
# RABBIT_URLS_OPEN = []
# RABBIT_USER_OPEN = 'esgf-publisher-open'
# IS_TEST = False
# data_node1 = 'foo'
# thredds_service_path1 = 'bar'
CONFIG_PATH = 'pid.ini'


def create_connector():

    config_dic = get_pid_conf(_get_config_fpath(CONFIG_PATH))
    # Information about one data node:
    trusted_node = {
        'user': config_dic['rabbit_user_trusted'],
        'password': config_dic['rabbit_password_trusted'],
        'url': config_dic['rabbit_url_trusted'],
        'priority': 1
    }
    open_node = {
        'user': config_dic['rabbit_user_open'],
        'url': config_dic['rabbit_urls_open']
    }

    list_cred = [trusted_node, open_node]

    # Initialize library for that data node:
    return esgfpid.Connector(
            messaging_service_credentials=list_cred,
            handle_prefix=config_dic['prefix'],
            messaging_service_exchange_name=config_dic['rabbit_exchange'],
            data_node=config_dic['data_node1'],
            thredds_service_path=config_dic['thredds_service_path1'],
            test_publication=config_dic['is_test']
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
    logging.info('Adding errata to {} version {}'.format(drs_id[0], drs_id[1]))
    connector.add_errata_ids(errata_ids=errata_id_list, drs_id=drs_id[0], version_number=drs_id[1])
    logging.info('Handle successfully updated.')


def remove_errata_from_handle(dataset_id, errata_id_list, connector):
    """
    given pid connector removes errata_id from handle
    :param dataset_id: dataset drs + version separated by '#'
    :param errata_id_list: the uid of the issue
    :param connector: RabbitMQ connector
    :return: nada
    """
    drs_id = dataset_id.split('#')
    logging.info('Removing errata id from {}, version {}'.format(drs_id[0], drs_id[1]))
    connector.remove_errata_ids(errata_ids=errata_id_list, drs_id=drs_id[0], version_number=drs_id[1])
    logging.info('Handle successfully updated.')


def get_pid_conf(config_path):
    """
    retrieves data mandatory for pid connection establishment.
    :return: dictionary of conf
    """
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    return config._sections['PID']
