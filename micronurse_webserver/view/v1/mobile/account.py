import base64

from django.core.cache import cache
from django.utils import translation
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request

from micronurse_webserver.models import Account
from micronurse_webserver.utils import view_utils, check_utils
from micronurse_webserver.view import authentication, result_code
from micronurse_webserver.view.check_exception import CheckException

CACHE_KEY_MOBILE_TOKEN = 'mobile_token'
MOBILE_TOKEN_VALID_HOURS = 120


def token_check(req: Request):
    try:
        token = req.META['HTTP_AUTH_TOKEN']
        phone_number = authentication.parse_token(token)
    except:
        raise CheckException(status_code=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache_token = cache.get(CACHE_KEY_MOBILE_TOKEN + phone_number)
    if token != cache_token:
        raise CheckException(status_code=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache.set(CACHE_KEY_MOBILE_TOKEN + phone_number, cache_token, MOBILE_TOKEN_VALID_HOURS * 3600)
    return Account(phone_number=phone_number)


@api_view(['PUT'])
def login(request: Request):
    try:
        print('Language code:', request.LANGUAGE_CODE)
        account = Account.objects.filter(phone_number=request.data['phone_number']).get()
        if not account.password == request.data['password']:
            raise CheckException(result_code=result_code.MOBILE_LOGIN_INCORRECT_PASSWORD,
                                 message=_('Incorrect password'), status=status.HTTP_401_UNAUTHORIZED)
        token_str = authentication.get_token(account.phone_number)
        cache.set(CACHE_KEY_MOBILE_TOKEN + account.phone_number, token_str, MOBILE_TOKEN_VALID_HOURS * 3600)
        res = view_utils.get_json_response(result_code=result_code.SUCCESS, message=_('Login successfully'),
                                           status=status.HTTP_201_CREATED, token=token_str)
        return res
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_LOGIN_USER_NOT_EXIST, message=_('User does not exist'),
                             status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_user_basic_info_by_phone(req: Request, phone_number: str):
    try:
        user = Account.objects.filter(phone_number=phone_number).get()
        portrait_base64 = base64.b64encode(user.portrait).decode()
        return view_utils.get_json_response(
            user=dict(nickname=user.nickname, gender=user.gender, account_type=user.account_type,
                      portrait=portrait_base64))
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_RESULT_NOT_FOUND, message=_('User does not exist'),
                             status=status.HTTP_404_NOT_FOUND)

