from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from micronurse_webserver.models import Account
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view import authentication, result_code
from micronurse_webserver.view.check_exception import CheckException

IOT_TOKEN_VALID_HOURS = 72
CACHE_KEY_IOT_TOKEN_PREFIX = 'iot_token_'


def token_check(req: Request):
    try:
        print()
        token = req.META['HTTP_AUTH_TOKEN']
        phone_number = authentication.parse_token(token)
    except:
        raise CheckException(status_code=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache_token = cache.get(CACHE_KEY_IOT_TOKEN_PREFIX + phone_number)
    if token != cache_token:
        raise CheckException(status_code=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache.set(CACHE_KEY_IOT_TOKEN_PREFIX + phone_number, cache_token, IOT_TOKEN_VALID_HOURS * 3600)
    return Account(phone_number=phone_number)


@api_view(['PUT'])
def login(request: Request):
    try:
        account = Account.objects.filter(phone_number=request.data['phone_number']).get()
        if not account.password == request.data['password']:
            raise CheckException(result_code=result_code.IOT_LOGIN_INCORRECT_PASSWORD, message=_('Incorrect password'), status=status.HTTP_401_UNAUTHORIZED)
        if not account.account_type == 'O':
            raise CheckException(result_code=result_code.IOT_LOGIN_ACCOUNT_TYPE_ERROR, message=_('Only older can login'), status=422)
        token_str = authentication.get_token(account.phone_number)
        cache.set(CACHE_KEY_IOT_TOKEN_PREFIX + account.phone_number, token_str, IOT_TOKEN_VALID_HOURS * 3600)
        res = view_utils.get_json_response(result_code=result_code.SUCCESS, message=_('Login successfully'), status=status.HTTP_201_CREATED, token=token_str, nickname=account.nickname)
        return res
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.IOT_LOGIN_USER_NOT_EXIST, message=_('User does not exist'), status=status.HTTP_401_UNAUTHORIZED)


@api_view(['DELETE'])
def logout(req: Request):
    user = token_check(req)
    cache.delete(CACHE_KEY_IOT_TOKEN_PREFIX + user.phone_number)
    return Response(status=status.HTTP_204_NO_CONTENT)
