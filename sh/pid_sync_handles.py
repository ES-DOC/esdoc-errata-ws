# -*- coding: utf-8 -*-

"""
.. module:: pid_sync_handles.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Synchornizes PID handles with remote PID service.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import logging
import random
import time

import schedule

from b2handle.handleclient import EUDATHandleClient
from errata import db
from errata.handle_service import exceptions
from errata.handle_service.utils import resolve_input
from errata.utils import config
from errata.utils import constants
from errata.utils import logger
from errata.utils import pid_connector as pid



# Set logging levels.
logging.getLogger("pika").setLevel(logging.CRITICAL)
logging.getLogger("esgfpid").setLevel(logging.ERROR)

# Map of task type to handlers.
_TASK_HANDLERS = {
    constants.PID_ACTION_INSERT: pid.add_errata_to_handle,
    constants.PID_ACTION_DELETE: pid.remove_errata_from_handle
}

# Interval in seconds between executions.
_RETRY_INTERVAL = config.pid.sync_retry_interval_in_seconds



def _main():
    """Main entry point.

    """
    logger.log_pid("PID syncing: STARTS")
    with pid.get_session() as pid_connection:
        with db.session.create(commitable=True):
            for task in db.dao.get_pid_tasks():
                logger.log_pid('Syncing: {}'.format(task.dataset_id))
                task.status, task.error = _sync(pid_connection, task)
                task.try_count += 1
    logger.log_pid("PID syncing: COMPLETE")


def _sync(pid_connection, task):
    """Synchronizes a task with remote PID handle service.

    """
    try:
        # Check handle.
        logger.log_pid('... checking handle')
        _check_handle_status(task.dataset_id)

        # Update handle.
        logger.log_pid('... calling update task')
        task_handler = _TASK_HANDLERS[task.action]
        task_handler(task.dataset_id, [task.issue_uid], pid_connection)

    # ... managed exceptions
    except exceptions.HandleMismatch as err:
        logger.log_pid_warning(err)
        return constants.PID_TASK_STATE_ERROR, unicode(err)[:1023]

    # ... unmanaged exceptions
    except Exception as err:
        logger.log_pid_error(err)
        return constants.PID_TASK_STATE_ERROR, unicode(err)[:1023]

    return constants.PID_TASK_STATE_COMPLETE, None


def _check_handle_status(dataset_id):
    """Checks handle exists or not.

    :returns: Flag indicating whether handle status is such that it requires fiurther processing
    :rtype: bool

    """
    # Get handle information.
    handle_string = resolve_input(dataset_id)
    handle_client = EUDATHandleClient.instantiate_for_read_access()
    encoded_dict = handle_client.retrieve_handle_record(handle_string)

    # Error if not found.
    if encoded_dict is None:
        raise exceptions.HandleMismatch('Dataset {} has no published pid handle'.format(dataset_id))

    # Reformat handle information.
    handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}

    # Error if handle has no test value.
    if '_TEST' not in handle_record.keys():
        raise exceptions.HandleMismatch('TEST VALUE WAS NOT FOUND IN HANDLE, ABORTING....')

    # Error if handle record value.
    if handle_record['_TEST'].lower() != str(config.pid.is_test).lower():
        raise exceptions.HandleMismatch('Dataset {} has mismatched test status [{}] with pid connector'.format(dataset_id, handle_record['_TEST']))

    logger.log_pid('Dataset handle is on mode {}, as well as connector, validating...'.format(handle_record['_TEST']))


# Main entry point.
if __name__ == '__main__':
    schedule.every(_RETRY_INTERVAL).seconds.do(_main)
    while True:
        schedule.run_pending()
        time.sleep(1)
