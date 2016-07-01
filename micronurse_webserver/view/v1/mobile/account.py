from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from micronurse_webserver.view import authentication
from micronurse_webserver.serializer import result_code
from micronurse_webserver import utils
from micronurse_webserver.models import Account
from micronurse_webserver.view.check_exception import CheckException

CACHE_KEY_MOBILE_TOKEN = 'mobile_token'
MOBILE_TOKEN_VALID_HOURS = 120


def token_check(req: Request):
    try:
        token = req.META['HTTP_AUTH_TOKEN']
        phone_number = authentication.parse_token(token)
    except:
        raise CheckException(status_code=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED, message='Token Invalid')
    cache_token = cache.get(CACHE_KEY_MOBILE_TOKEN + phone_number)
    if token != cache_token:
        raise CheckException(status_code=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED, message='Token Invalid')
    cache.set(CACHE_KEY_MOBILE_TOKEN + phone_number, cache_token, MOBILE_TOKEN_VALID_HOURS * 3600)
    return Account(phone_number=phone_number)


@api_view(['PUT'])
def login(request: Request):
    try:
        account = Account.objects.filter(phone_number=request.data['phone_number']).get()
        if not account.password == request.data['password']:
            return utils.get_json_response(result_code=result_code.MOBILE_LOGIN_INCORRECT_PASSWORD, message='Password Incorrect', status=status.HTTP_401_UNAUTHORIZED)
        token_str = authentication.get_token(account.phone_number)
        cache.set(CACHE_KEY_MOBILE_TOKEN + account.phone_number, token_str, MOBILE_TOKEN_VALID_HOURS * 3600)
        res = utils.get_json_response(result_code=result_code.SUCCESS, message='Login Success', status=status.HTTP_201_CREATED, token=token_str)
        return res
    except Account.DoesNotExist:
        return utils.get_json_response(result_code=result_code.MOBILE_LOGIN_USER_NOT_EXIST, message='User Not Exists', status=status.HTTP_401_UNAUTHORIZED)