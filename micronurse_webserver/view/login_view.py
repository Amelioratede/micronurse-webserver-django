from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from micronurse_webserver.models import Account
from micronurse_webserver import utils


LOGIN_SUCCESS = 0
LOGIN_USER_NOT_EXISTS = 101
LOGIN_PASSWORD_INCORRECT = 102
LOGIN_TYPE_ERROR = 103
SESSION_ATTR_IOT_USER = 'iot_user'
CACHE_KEY_IOT_TOKEN = 'iot_token'
IOT_TOKEN_VALID_HOURS = 72

SESSION_ATTR_MOBILE_USER = 'mobile_user'
CACHE_KEY_MOBILE_TOKEN = 'mobile_token'
MOBILE_TOKEN_VALID_HOURS = 120

@csrf_exempt
def iot_login(req: HttpRequest):
    req_data = utils.post_check(req)
    try:
        account = Account.objects.filter(phone_number=req_data['phone_number']).get()
        if not account.password == req_data['password']:
            return utils.get_json_response(LOGIN_PASSWORD_INCORRECT, 'Password incorrect')
        if not account.account_type == 'O':
            return utils.get_json_response(LOGIN_TYPE_ERROR, 'Only older can login')
        req.session[SESSION_ATTR_IOT_USER] = account
        token_str = utils.get_token(account.phone_number)
        cache.set(CACHE_KEY_IOT_TOKEN + account.phone_number, token_str, IOT_TOKEN_VALID_HOURS * 3600)
        res = utils.get_json_response(LOGIN_SUCCESS, 'Login Success', token=token_str, nickname=account.nickname)
        return res
    except Account.DoesNotExist:
        return utils.get_json_response(LOGIN_USER_NOT_EXISTS, 'User not exists')

@csrf_exempt
def mobile_login(req: HttpRequest):
    req_data = utils.post_check(req)
    try:
        account = Account.objects.filter(phone_number=req_data['phone_number']).get()
        if not account.password == req_data['password']:
            return utils.get_json_response(LOGIN_PASSWORD_INCORRECT, 'Password incorrect')
        req.session[SESSION_ATTR_MOBILE_USER] = account
        token_str = utils.get_token(account.phone_number)
        cache.set(CACHE_KEY_MOBILE_TOKEN + account.phone_number, token_str, MOBILE_TOKEN_VALID_HOURS * 3600)
        res = utils.get_json_response(LOGIN_SUCCESS, 'Login Success', token=token_str, nickname=account.nickname,
                                      account_type=account.account_type)
        return res
    except Account.DoesNotExist:
        return utils.get_json_response(LOGIN_USER_NOT_EXISTS, 'User not exists')