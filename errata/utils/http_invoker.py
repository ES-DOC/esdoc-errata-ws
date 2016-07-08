# -*- coding: utf-8 -*-
"""
.. module:: utils.http_invoker.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - http invocation functions.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>


"""
from errata.utils import logger
from errata.utils.convert import to_dict
from errata.utils.convert import to_camel_case



# Processing error HTTP response code.
_HTTP_RESPONSE_SERVER_ERROR = 500


def _can_return_debug_info(handler):
    """Gets flag indicating whether the application can retrun debug information.

    """
    return handler.application.settings.get('debug', False)


def _log_error(handler, error):
    """Logs an error response.

    """
    msg = "[{0}]: --> error --> {1} --> {2}"
    msg = msg.format(id(handler), handler, error)
    logger.log_web_error(msg)


def _log_success(handler):
    """Logs a successful response.

    """
    msg = "[{0}]: success --> {1}"
    msg = msg.format(id(handler), handler)
    logger.log_web(msg)


def _write(handler, data):
    """Writes HTTP response data.

    """
    # Log begin.
    msg = "[{0}]: response writing begins --> {1}"
    msg = msg.format(id(handler), handler)
    logger.log_web(msg)

    # Write response.
    handler.write(to_dict(data, to_camel_case))

    # Set HTTP header.
    handler.set_header("Content-Type", "application/json; charset=utf-8")

    # Log end.
    msg = "[{0}]: response writing ends --> {1}"
    msg = msg.format(id(handler), handler)
    logger.log_web(msg)


def _write_error(handler, error):
    """Writes processing error to response stream.

    """
    handler.clear()
    reason = unicode(error) if _can_return_debug_info(handler) else None
    handler.send_error(_HTTP_RESPONSE_SERVER_ERROR, reason=reason)


def _write_success(handler):
    """Writes processing success to response stream.

    """
    try:
        data = handler.output
    except AttributeError:
        data = {}
    if 'status' not in data:
        data['status'] = 0

    _write(handler, data)


def _get_tasks(tasks, defaults):
    """Returns formatted & extended taskset.

    """
    try:
        iter(tasks)
    except TypeError:
        tasks = [tasks]

    return tasks + defaults


def _invoke(handler, task, err=None):
    """Invokes a task.

    """
    try:
        if err:
            task(handler, err)
        else:
            task(handler)
    except TypeError:
        if err:
            task(err)
        else:
            task()


def execute(handler, tasks, error_tasks):
    """Invokes a set of HTTP request processing tasks.

    :param HTTPRequestHandler handler: Request processing handler.
    :param list tasks: Collection of processing tasks.
    :param list error_tasks: Collection of error processing tasks.

    """
    # Extend tasks.
    tasks = _get_tasks(tasks, [_log_success, _write_success])
    error_tasks = _get_tasks(error_tasks, [_log_error, _write_error])

    # Invoke normal processing tasks.
    for task in tasks:
        try:
            _invoke(handler, task)
        except Exception as err:
            # Invoke error processing tasks.
            try:
                for task in error_tasks:
                    _invoke(handler, task, err)
            # ... suppress inner exceptions.
            except Exception:
                pass
            finally:
                return err
