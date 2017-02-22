# -*- coding: utf-8 -*-
"""
.. module:: utils.pid_connector.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Encapsualtes interactions with remote PID service.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import esgfpid

from errata.utils import config
from errata.utils import logger



def create_connector():
    """Instantiates & returns a connection to a PID server.

    :returns: A connection to a PID server.
    :rtype: esgfpid.Connector

    """
    # Information about nodes:
    trusted_node = {
        'password': config.pid.rabbit_password_trusted,
        'priority': 1,
        'url': config.pid.rabbit_url_trusted,
        'user': config.pid.rabbit_user_trusted
    }
    open_node = {
        'url': config.pid.rabbit_urls_open,
        'user': config.pid.rabbit_user_open
    }

    # Return connection for that data node:
    return esgfpid.Connector(
        messaging_service_credentials=[trusted_node, open_node],
        handle_prefix=config.pid.prefix,
        messaging_service_exchange_name=config.pid.rabbit_exchange,
        data_node=config.pid.data_node1,
        thredds_service_path=config.pid.thredds_service_path1,
        test_publication=config.pid.is_test
        )


def add_errata_to_handle(dataset_id, errata_ids, connector):
    """Adds an errata identifier to a pid handle.

    :param str dataset_id: dataset drs + version separated by '#'
    :param errata_ids: the uid of the issue
    :param esgfpid.Connector connector: PID RabbitMQ connector

    """
    drs_id = dataset_id.split('#')
    logger.log_pid('Adding errata to {} version {}'.format(drs_id[0], drs_id[1]))
    connector.add_errata_ids(errata_ids=errata_ids, drs_id=drs_id[0], version_number=drs_id[1])
    logger.log_pid('Handle successfully updated.')


def remove_errata_from_handle(dataset_id, errata_ids, connector):
    """Removes an errata identifier from pid handle.

    :param str dataset_id: dataset drs + version separated by '#'
    :param list errata_ids: the uid of the issue
    :param esgfpid.Connector connector: PID RabbitMQ connector

    """
    drs_id = dataset_id.split('#')
    logger.log_pid('Removing errata id from {}, version {}'.format(drs_id[0], drs_id[1]))
    connector.remove_errata_ids(errata_ids=errata_ids, drs_id=drs_id[0], version_number=drs_id[1])
    logger.log_pid('Handle successfully updated.')
