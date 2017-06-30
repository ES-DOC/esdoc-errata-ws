# -*- coding: utf-8 -*-
"""
.. module:: utils.pid_connector.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Encapsualtes interactions with remote PID service.

.. moduleauthor:: Atef Ben Nasser <abenasser@ipsl.jussieu.fr>


"""
import contextlib

import esgfpid

from errata.utils import config
from errata.utils import logger


@contextlib.contextmanager
def get_session():
    """Starts & manages a pid-handle-server session.
    """
    connection = create_connector()
    connection.start_messaging_thread()
    logger.log_pid("PID service connection [{}] opened".format(id(connection)))
    try:
        yield connection
    except Exception as err:
        msg = "An unhandled exception occurred within the context of a PID service connection: {}."
        msg = msg.format(err)
        logger.log_pid_error(msg)
        raise err
    finally:
        try:
            connection.finish_messaging_thread()
        except:
            pass
        else:
            logger.log_pid("PID service connection [{}] closed".format(id(connection)))


def create_connector():
    """Instantiates & returns a connection to a PID server.

    :returns: A connection to a PID server.
    :rtype: esgfpid.Connector

    """
    # Information about rabbitmq instance:
    cred = dict(user=config.pid.rabbit_user_trusted, password=config.pid.rabbit_password_trusted,
                url=config.pid.rabbit_url_trusted, vhost=config.pid.vhost, port=config.pid.port)
    # Return connection for that data node:
    return esgfpid.Connector(
        messaging_service_credentials=[cred],
        handle_prefix=config.pid.prefix,
        messaging_service_exchange_name=config.pid.rabbit_exchange,
        data_node=config.pid.data_node1,
        test_publication=config.pid.is_test,
        thredds_service_path=config.pid.thredds_service_path1,
        message_service_synchronous=config.pid.is_synchronous
        )


def add_errata_to_handle(dataset_id, errata_ids, connector):
    """Adds an errata identifier to a pid handle.

    :param str dataset_id: dataset drs + version separated by '#'
    :param errata_ids: the uid of the issue
    :param esgfpid.Connector connector: PID RabbitMQ connector

    """
    if '#' in dataset_id:
        drs_id = dataset_id.split('#')
    elif '.v' in dataset_id:
        drs_id = dataset_id.replace('.v', '.#')
        drs_id = drs_id.split('#')
    else:
        raise Exception('Could not extract version number from dataset id. Aborting. {}'.format(dataset_id))
    if len(drs_id) == 2:
        for errata in errata_ids:
            logger.log_pid('Adding errata {} to {} version {}'.format(errata, drs_id[0], drs_id[1]))
        connector.add_errata_ids(errata_ids=errata_ids, drs_id=drs_id[0], version_number=drs_id[1])
        logger.log_pid('Handle successfully updated.')
    else:
        raise Exception('Could not extract version number from dataset id. Aborting. {}'.format(dataset_id))


def remove_errata_from_handle(dataset_id, errata_ids, connector):
    """Removes an errata identifier from pid handle.

    :param str dataset_id: dataset drs + version separated by '#'
    :param list errata_ids: the uid of the issue
    :param esgfpid.Connector connector: PID RabbitMQ connector

    """
    if '#' in dataset_id:
        drs_id = dataset_id.split('#')
    elif '.v' in dataset_id:
        drs_id = dataset_id.replace('.v', '.#')
        drs_id = drs_id.split('#')
    else:
        raise Exception('Could not extract version number from dataset id. Aborting. {}'.format(dataset_id))
    if len(drs_id) == 2:
        logger.log_pid('Removing errata id from {}, version {}'.format(drs_id[0], drs_id[1]))
        connector.remove_errata_ids(errata_ids=errata_ids, drs_id=drs_id[0], version_number=drs_id[1])
        logger.log_pid('Handle successfully updated.')
    else:
        raise Exception('Could not extract version number from dataset id. Aborting. {}'.format(dataset_id))
