from errata_ws.utils import logger
from errata_ws.utils import constants
from errata_ws.utils.convertor import to_dict
from errata_ws.utils.convertor import to_camel_case
from errata_ws.utils.exceptions import ERROR_CODES
from errata_ws.utils.http_security import secure_request
from errata_ws.utils.http_validator import validate_request



def process_request(handler, tasks_exec, tasks_error=None):
    """Invokes a set of HTTP request processing tasks.

    :param HTTPRequestHandler handler: Request processing handler.
    :param list tasks: Collection of processing tasks.
    :param list error_tasks: Collection of error processing tasks.

    """
    # Set execution tasks.
    tasks_exec_pre = [_log_begin, secure_request, validate_request]
    tasks_exec_post = [_log_success, _write_success]
    tasks_exec = _get_tasks(tasks_exec_pre, tasks_exec, tasks_exec_post)

    # Set error tasks.
    tasks_error_pre = []
    tasks_error_post = [_log_error, write_error]
    tasks_error = _get_tasks(tasks_error_pre, tasks_error or [], tasks_error_post)

    # Invoke tasksets.
    for task in tasks_exec:
        try:
            _invoke_task(handler, task)
        except Exception as err:
            try:
                for task in tasks_error:
                    _invoke_task(handler, task, err)
            except:
                # suppress error processing exceptions
                pass
            break


def _get_tasks(tasks_pre, tasks, tasks_post):
    """Returns formatted & extended taskset.

    """
    try:
        iter(tasks)
    except TypeError:
        tasks = [tasks]

    return tasks_pre + tasks + tasks_post


def _invoke_task(handler, task, err=None):
    """Invokes a task.

    """
    try:
        if err:
            task(handler, err)
        else:
            task(handler)
    except TypeError as te:
        if err:
            task(err)
        else:
            task()


def _log(handler, msg, is_error=False):
    """Logs an error response.

    """
    msg = "[{}]: --> {}".format(id(handler), msg)
    if is_error:
        logger.log_web_error(msg)
    else:
        logger.log_web(msg)


def _log_begin(handler):
    """Logs beginning of request processing.

    """
    msg = "[{0}]: executing --> {1}"
    msg = msg.format(id(handler), handler)
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


def _write(handler, data, encoding='json'):
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

    # Set error info to be returned to client.
    _write(handler, {
        'error_code': ERROR_CODES.get(type(error), 999),
        'error_field': getattr(error, 'field', '--'),
        'error_message': error.message.strip(),
        'error_type': type(error).__name__
    })

    # Set response HTTP status code.
    try:
        handler.set_status(error.response_code)
    except AttributeError:
        handler.set_status(constants.HTTP_RESPONSE_SERVER_ERROR)


def _write_success(handler):
    """Writes processing success to response stream.

    """
    # Set response encoding.
    try:
        encoding = handler.output_encoding
    except AttributeError:
        encoding = 'json'

    # Set response data.
    try:
        data = handler.output
    except AttributeError:
        data = unicode()
        encoding = None

    # Write respponse.
    _write(handler, data, encoding)

    # Clean up.
    try:
        del handler.output
    except AttributeError:
        pass
