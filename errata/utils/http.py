# -*- coding: utf-8 -*-
"""
.. module:: utils.http.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: HTTP utility functions, particulary process_request.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.utils import exceptions
from errata.utils.http_security import secure_request
from errata.utils.http_validator import validate_request
from errata.utils import logger
from errata.utils.convertor import to_dict
from errata.utils.convertor import to_camel_case



# Request validation error HTTP response code.
_HTTP_RESPONSE_INVALID_REQUEST_ERROR = 400

# Processing error HTTP response code.
_HTTP_RESPONSE_SERVER_ERROR = 500


def _can_return_debug_info(handler):
    """Gets flag indicating whether the application can retrun debug information.

    """
    return handler.application.settings.get('debug', False)


def _log(handler, msg, is_error=False):
    """Logs an error response.

    """
    msg = "[{}]: --> {}".format(id(handler), msg)
    if is_error:
        logger.log_web_error(msg)
    else:
        logger.log_web(msg)


def _log_error(handler, error):
    """Logs an error response.

    """
    _log(handler, "error --> {} --> {}".format(handler, error), True)


def _log_success(handler):
    """Logs a successful response.

    """
    _log(handler, "success --> {}".format(handler))


def _write_null(handler, data):
    """Writes HTTP response null data.

    """
    pass


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
    None: _write_null,
    'csv': _write_csv,
    'json': _write_json,
    'html': _write_html,
    'pdf': _write_pdf,
    'xml': _write_xml
}


def _write(handler, data, encoding):
    """Writes HTTP response data.

    """
    # Log begin.
    _log(handler, "response writing begins --> {}".format(handler))

    # Write.
    _WRITERS[encoding](handler, data)

    # Log end.
    _log(handler, "response writing ends --> {}".format(handler))


def write_error(handler, error):
    """Writes processing error to response stream.

    """
    # Reset handler output.
    handler.clear()

    # Set reason code (exception shielding when not in PROD).
    reason = unicode(error) if _can_return_debug_info(handler) else None

    # Set resoponse code.
    if isinstance(error, exceptions.WebServiceError):
        response_code = error.response_code
    else:
        response_code = _HTTP_RESPONSE_SERVER_ERROR

    # Return error.
    handler.send_error(response_code, reason=reason.replace("\n", ""))


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
        data = unicode()
        encoding = None

    _write(handler, data, encoding)

    try:
        handler.output
    except AttributeError:
        pass
    else:
        del handler.output


def _get_tasks(pre_tasks, tasks, post_tasks):
    """Returns formatted & extended taskset.

    """
    try:
        iter(tasks)
    except TypeError:
        tasks = [tasks]

    return pre_tasks + tasks + post_tasks


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


def process_request(handler, tasks, error_tasks=None):
    """Invokes a set of HTTP request processing tasks.

    :param HTTPRequestHandler handler: Request processing handler.
    :param list tasks: Collection of processing tasks.
    :param list error_tasks: Collection of error processing tasks.

    """
    # Log request.
    msg = "[{0}]: executing --> {1}"
    msg = msg.format(id(handler), handler)
    logger.log_web(msg)

    # Extend tasksets.
    tasks = _get_tasks(
        [secure_request, validate_request],
        tasks,
        [_log_success, _write_success]
        )
    error_tasks = _get_tasks(
        [],
        error_tasks or [],
        [_log_error, write_error]
        )

    # Invoke tasksets:
    # ... normal processing;
    for task in tasks:
        try:
            _invoke(handler, task)
        except Exception as err:
            # ... error processing;
            try:
                for task in error_tasks:
                    _invoke(handler, task, err)
            # ... error processing exceptions are suppressed
            except:
                pass
            break
