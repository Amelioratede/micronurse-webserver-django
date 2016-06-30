import traceback

from django.http import Http404
from rest_framework.exceptions import APIException

import micronurse_webserver.utils
import micronurse_webserver.view.authentication
from micronurse_webserver import utils
from micronurse_webserver.view.check_exception import CheckException


def custom_exception_handler(exc, context):
    traceback.print_exc()
    status = 0
    result_code = 0
    message = ''
    if isinstance(exc, Http404):
        status = result_code = 404
        message = 'API Not Found'
    elif isinstance(exc, CheckException):
        status = exc.status_code
        result_code = exc.result_code
        message = exc.detail
    elif isinstance(exc, APIException):
        status = result_code = exc.status_code
        message = exc.detail
    elif isinstance(exc, KeyError):
        status = result_code = 400
        message = "Bad Request"
    else:
        status = result_code = 500
        message = 'Server Internal Error'
    return micronurse_webserver.utils.get_json_response(result_code=result_code, message=message, status=status)