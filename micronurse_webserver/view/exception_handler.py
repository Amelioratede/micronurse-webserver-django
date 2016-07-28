import traceback

from django.http import Http404
from django.utils.translation import ugettext as _
from rest_framework.exceptions import APIException, MethodNotAllowed

from micronurse_webserver.utils import view_utils
from micronurse_webserver.view.check_exception import CheckException


def custom_exception_handler(exc, context):
    traceback.print_exc()
    if isinstance(exc, Http404):
        status = result_code = 404
        message = _('API not found')
    elif isinstance(exc, CheckException):
        status = exc.status
        result_code = exc.result_code
        message = exc.detail
    elif isinstance(exc, APIException):
        status = result_code = exc.status_code
        message = exc.detail
    elif isinstance(exc, KeyError):
        status = result_code = 400
        message = _("Bad request")
    else:
        status = result_code = 500
        message = _('Server internal error')
    return view_utils.get_json_response(result_code=result_code, message=message, status=status)