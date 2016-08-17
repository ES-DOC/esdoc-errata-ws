# -*- coding: utf-8 -*-
"""
.. module:: utils.http_invoker.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: HTTP request handler task invoker.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.utils import http_logger as logger
from errata.utils.convertor import to_dict
from errata.utils.convertor import to_camel_case



# Processing error HTTP response code.
_HTTP_RESPONSE_SERVER_ERROR = 500


def _can_return_debug_info(handler):
    """Gets flag indicating whether the application can retrun debug information.

    """
    return handler.application.settings.get('debug', False)


def _write_csv(handler, data):
    """Writes HTTP response CSV data.

    """
    handler.write(data)
    handler.set_header("Content-Type", "application/csv; charset=utf-8")


def _write_json(handler, data):
    """Writes HTTP response JSON data.

    """
    handler.write(to_dict(data, to_camel_case))
    handler.set_header("Content-Type", "application/json; charset=utf-8")


def _write_html(handler, data):
    """Writes HTTP response HTML data.

    """
    handler.write(data)
    handler.set_header("Content-Type", "text/html; charset=utf-8")


def _write_pdf(handler, data):
    """Writes HTTP response PDF data.

    """
    handler.write(data)
    handler.set_header("Content-Type", "application/pdf; charset=utf-8")


def _write_xml(handler, data):
    """Writes HTTP response XML data.

    """
    handler.write(data)
    handler.set_header("Content-Type", "application/xml; charset=utf-8")


# Map of response writers to encodings.
_WRITERS = {
    'csv': _write_csv,
    'json': _write_json,
    'html': _write_html,
    'pdf': _write_pdf,
    'xml': _write_xml
}


def _write(handler, data, encoding='json'):
    """Writes HTTP response data.

    """
    # Log begin.
    logger.log(handler, "response writing begins --> {}".format(handler))

    # Write.
    _WRITERS[encoding](handler, data)

    # Log end.
    logger.log(handler, "response writing ends --> {}".format(handler))


def write_error(handler, error):
    """Writes processing error to response stream.

    """
    handler.clear()
    reason = unicode(error) if _can_return_debug_info(handler) else None
    handler.send_error(_HTTP_RESPONSE_SERVER_ERROR, reason=reason)


def _write_success(handler):
    """Writes processing success to response stream.

    """
    try:
        encoding = handler.output_encoding
    except AttributeError:
        encoding = 'json'

    try:
        data = handler.output
    except AttributeError:
        data = {} if encoding == 'json' else unicode()

    if encoding == 'json' and 'status' not in data:
        data['status'] = 0

    _write(handler, data, encoding)


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
    tasks = _get_tasks(tasks, [logger.log_success, _write_success])
    error_tasks = _get_tasks(error_tasks, [logger.log_error, write_error])

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
