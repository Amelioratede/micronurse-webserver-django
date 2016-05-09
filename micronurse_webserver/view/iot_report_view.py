from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from micronurse_webserver import utils
from .login_view import SESSION_ATTR_IOT_USER
from .login_view import CACHE_KEY_IOT_TOKEN


@csrf_exempt
def report(request: HttpRequest):
    utils.post_check(request, CACHE_KEY_IOT_TOKEN + request.session.get(SESSION_ATTR_IOT_USER))
    print('Data:' + str(request.POST['data']))
    return utils.get_json_response(0, "Report successfully")