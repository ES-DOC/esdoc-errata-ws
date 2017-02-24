# -*- coding: utf-8 -*-

"""
.. module:: pid_sync_handles.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Inserts test issues into the errata db.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import logging
import time

import schedule

from errata import db
from errata.utils import config
from errata.utils import constants
from errata.utils import logger
from errata.utils import pid_connector as pid



# Set logging levels.
logging.getLogger("pika").setLevel(logging.CRITICAL)
logging.getLogger("esgfpid").setLevel(logging.ERROR)

# Interval in seconds between executions.
_RETRY_INTERVAL = config.pid.sync_retry_interval_in_seconds

# Map of task type to handlers.
_TASK_HANDLERS = {
    constants.PID_ACTION_INSERT: pid.add_errata_to_handle,
    constants.PID_ACTION_DELETE: pid.remove_errata_from_handle
}


def _sync(pid_connection, task):
    """Synchronizes a task with remote PID handle service.

    """
    try:
        handler = _TASK_HANDLERS[task.action]
        handler(task.dataset_id, task.issue_uid, pid_connection)
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
    schedule.every(_RETRY_INTERVAL).seconds.do(_main)
    while True:
        schedule.run_pending()
        time.sleep(1)
