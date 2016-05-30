# -*- coding: utf-8 -*-
"""
.. module:: utils.http.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - http utility functions.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>


"""
import json
import uuid

import cerberus
import tornado

from errata.utils.convert import to_dict
from errata.utils.convert import to_namedtuple
from errata.utils.convert import to_camel_case
from errata.utils import logger



# Http response codes.
_HTTP_RESPONSE_BAD_REQUEST = 400
_HTTP_RESPONSE_SERVER_ERROR = 500

# HTTP CORS header.
HTTP_HEADER_Access_Control_Allow_Origin = "Access-Control-Allow-Origin"


class _RequestValidator(cerberus.Validator):
    def _validate_type_uuid(self, field, value):
        """Enables validation for `uuid` schema attribute.

        :param field: field name.
        :param value: field value.

        """
        try:
            uuid.UUID(value)
        except ValueError:
            self._error(field, cerberus.errors.ERROR_BAD_TYPE.format('uuid'))


class HTTPRequestHandler(tornado.web.RequestHandler):
    """A web service request handler.

    """
    @property
    def _can_return_debug_info(self):
        """Gets flag indicating whether the application can retrun debug information.

        """
        return self.application.settings.get('debug', False)


    def decode_json_body(self, as_namedtuple=True):
        """Decodes request body JSON string.

        :param tornado.web.RequestHandler handler: A web request handler.

        :returns: Decoded json data.
        :rtype: namedtuple | None

        """
        if not self.request.body:
            return None

        body = json.loads(self.request.body)

        return to_namedtuple(body) if as_namedtuple else body


    def invoke(
        self,
        validation_schema,
        processing_taskset,
        processing_error_taskset=[],
        write_raw_output=False
        ):
        """Invokes handler tasks.

        """
        def _write(data):
            """Writes HTTP response data.

            """
            msg = "[{0}]: response writing begins --> {1}"
            msg = msg.format(id(self), self)
            logger.log_web(msg)

            # Write response.
            if write_raw_output:
                self.write(data)
            else:
                self.write(to_dict(data, to_camel_case))

            # Set HTTP header.
            self.set_header("Content-Type", "application/json; charset=utf-8")

            msg = "[{0}]: response writing ends --> {1}"
            msg = msg.format(id(self), self)
            logger.log_web(msg)


        def _write_error(http_status_code, err):
            """Writes error response.

            """
            self.clear()
            reason = unicode(err) if self._can_return_debug_info else None
            self.send_error(http_status_code, reason=reason)


        def _write_invalid_request(err):
            """Writes request validation error.

            """
            self.clear()
            _write_error(_HTTP_RESPONSE_BAD_REQUEST, err)


        def _write_success():
            """Writes processing success to response stream.

            """
            try:
                data = self.output
            except AttributeError:
                data = {}
            if 'status' not in data:
                data['status'] = 0
            _write(data)


        def _write_failure(err):
            """Writes processing failure to response stream.

            """
            self.clear()
            _write_error(_HTTP_RESPONSE_SERVER_ERROR, err)


        def _log_start():
            """Logs start of request processing.

            """
            msg = "[{0}]: executing --> {1}"
            msg = msg.format(id(self), self)
            logger.log_web(msg)


        def _log_success():
            """Logs a successful response.

            """
            msg = "[{0}]: success --> {1}"
            msg = msg.format(id(self), self)
            logger.log_web(msg)


        def _log_error(error):
            """Logs an error response.

            """
            msg = "[{0}]: --> error --> {1} --> {2}"
            msg = msg.format(id(self), self, error)
            logger.log_web_error(msg)


        def _log_security(error):
            """Logs a security related response.

            """
            msg = "[{0}]: --> security --> {1} --> {2}"
            msg = msg.format(id(self), self, error)
            logger.log_web_security(msg)


        def _get_taskset(taskset):
            """Returns formatted & extended taskset.

            """
            try:
                iter(taskset)
            except TypeError:
                return [taskset]
            return taskset


        def _invoke(task, err=None):
            """Invokes a task.

            """
            try:
                if err:
                    task(self, err)
                else:
                    task(self)
            except TypeError:
                if err:
                    task(err)
                else:
                    task()


        def _invoke_taskset(taskset, error_taskset):
            """Invokes a set of tasks.

            """
            for task in taskset:
                try:
                    _invoke(task)
                except Exception as err:
                    try:
                        for error_task in error_taskset:
                            _invoke(error_task, err)
                    # ... suppress inner exceptions.
                    except Exception:
                        pass
                    return err


        # Log start.
        _log_start()

        # Validate request.
        v = _RequestValidator(validation_schema or dict())
        if not v.validate(self.request.query_arguments):
            _log_security("Invalid request :: {}".format(v.errors))
            self.clear()
            self.send_error(_HTTP_RESPONSE_BAD_REQUEST)
            return

        # Set green-line taskset.
        taskset = _get_taskset(processing_taskset)
        taskset.append(_log_success)
        taskset.append(_write_success)

        # Set red-line taskset.
        error_taskset = _get_taskset(processing_error_taskset)
        error_taskset.append(_log_error)
        error_taskset.append(_write_failure)

        # Invoke taskset(s).
        _invoke_taskset(taskset, error_taskset)
