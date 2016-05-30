from django.core.cache import cache
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

from micronurse_webserver import utils
from micronurse_webserver.view.login_view import SESSION_ATTR_IOT_USER, CACHE_KEY_IOT_TOKEN, IOT_TOKEN_VALID_HOURS, MOBILE_TOKEN_VALID_HOURS

LOGOUT_SUCCESS = 0
LOGOUT_USER_INCORRECT = 100

@csrf_exempt
def iot_logout(request: HttpRequest):
    account = request.session[SESSION_ATTR_IOT_USER];
    data = utils.post_check(request, CACHE_KEY_IOT_TOKEN + account.phone_number, IOT_TOKEN_VALID_HOURS)
    if data['phone_number'] != account.phone_number:
        return utils.get_json_response(LOGOUT_USER_INCORRECT, 'User info check failed')
    print('' + account.phone_number + ' logout.')
    cache.delete(CACHE_KEY_IOT_TOKEN + account.phone_number)
    del request.session[SESSION_ATTR_IOT_USER]
    return utils.get_json_response(LOGOUT_SUCCESS, 'Logout success')
