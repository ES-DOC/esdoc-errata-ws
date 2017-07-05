# -*- coding: utf-8 -*-

"""
.. module:: pid_sync_handles.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Inserts test issues into the errata db.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import logging

from errata import db
from errata.utils import constants
from errata.utils import logger
from errata.utils import pid_connector as pid
from b2handle.handleclient import EUDATHandleClient
from errata.utils import config
from errata.handle_service.utils import resolve_input
from errata.handle_service import exceptions

# Set logging levels.
logging.getLogger("pika").setLevel(logging.CRITICAL)
logging.getLogger("esgfpid").setLevel(logging.ERROR)

# Map of task type to handlers.
_TASK_HANDLERS = {
    constants.PID_ACTION_INSERT: pid.add_errata_to_handle,
    constants.PID_ACTION_DELETE: pid.remove_errata_from_handle
}


def _check_handle_status(dataset_id):
    """
    Checks handle exists or not.
    Checks is_test status.
    :return: Boolean
    """
    handle_string = resolve_input(dataset_id)
    handle_client = EUDATHandleClient.instantiate_for_read_access()
    encoded_dict = handle_client.retrieve_handle_record(handle_string)
    if encoded_dict is not None:
        handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
        if '_TEST' in handle_record.keys():
            if handle_record['_TEST'].lower() != str(config.pid.is_test).lower():
                logger.warn('Dataset {} has mismatched test status with pid connector'.format(dataset_id))
                logger.warn('Dataset {} is published with test flag {}'.format(dataset_id, handle_record['_TEST']))
                return False
        else:
            logger.log_pid('Dataset handle is on mode {}, as well as connector, validating...'.format(handle_record['_TEST']))
            return True
    else:
        logger.warn('Dataset {} has no published pid handle'.format(dataset_id))
        return False


def _sync(pid_connection, task):
    """Synchronizes a task with remote PID handle service.

    """
    logging.info('Syncing...')
    logger.log_pid(task.dataset_id)
    try:
        handler = _TASK_HANDLERS[task.action]
        logger.log_pid('CHECKING HANDLE...')
        if _check_handle_status(task.dataset_id):
            logger.log_pid('HANDLE FOUND...')
            logger.log_pid('Calling update task...')
            handler(task.dataset_id, [task.issue_uid], pid_connection)
        else:
            raise exceptions.HandleMismatch
    except Exception as err:
        logger.log_pid_error(err)
        task.status = constants.PID_TASK_STATE_ERROR
        task.error = unicode(err)[:1023]
    else:
        task.status = constants.PID_TASK_STATE_COMPLETE
    finally:
        task.try_count += 1


def _main():
    """Main entry point.

    """
    logger.log_pid("PID syncing: STARTS")
    with pid.get_session() as pid_connection:
        with db.session.create(commitable=True):
            for task in db.dao.get_pid_service_tasks():
                _sync(pid_connection, task)
    logger.log_pid("PID syncing: COMPLETE")


# Main entry point.
if __name__ == '__main__':
    _main()
