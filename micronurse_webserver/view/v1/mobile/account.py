import base64
import os

from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from micronurse.settings import BASE_DIR
from micronurse_webserver.models import Account
from micronurse_webserver.utils import view_utils, check_utils
from micronurse_webserver.view import authentication, result_code
from micronurse_webserver.view.check_exception import CheckException

CACHE_KEY_MOBILE_TOKEN_PREFIX = 'mobile_token_'
MOBILE_TOKEN_VALID_HOURS = 120


def token_check(req: Request):
    try:
        token = req.META['HTTP_AUTH_TOKEN']
        phone_number = authentication.parse_token(token)
    except Exception:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache_token = cache.get(CACHE_KEY_MOBILE_TOKEN_PREFIX + phone_number)
    if token != cache_token:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache.set(CACHE_KEY_MOBILE_TOKEN_PREFIX + phone_number, cache_token, MOBILE_TOKEN_VALID_HOURS * 3600)
    return Account(phone_number=phone_number)


@api_view(['PUT'])
def login(request: Request):
    try:
        account = Account.objects.filter(phone_number=request.data['phone_number']).get()
        if not account.password == request.data['password']:
            raise CheckException(result_code=result_code.MOBILE_LOGIN_INCORRECT_PASSWORD,
                                 message=_('Incorrect password'), status=status.HTTP_401_UNAUTHORIZED)
        token_str = authentication.get_token(account.phone_number)
        cache.set(CACHE_KEY_MOBILE_TOKEN_PREFIX + account.phone_number, token_str, MOBILE_TOKEN_VALID_HOURS * 3600)
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


@api_view(['DELETE'])
def logout(req: Request):
    user = token_check(req)
    cache.delete(CACHE_KEY_MOBILE_TOKEN_PREFIX + user.phone_number)
    return Response(status=status.HTTP_204_NO_CONTENT)


def read_default_portrait():
    img_file = open(os.path.join(BASE_DIR, 'micronurse_webserver/default-portrait'), 'rb')
    return bytes(img_file.read())


@api_view(['POST'])
def register(req: Request):
    if not check_utils.check_phone_num(phone_num=req.data['phone_number']):
        raise CheckException(result_code=result_code.MOBILE_PHONE_NUM_INVALID, message=_('Invalid phone number'))
    if Account.objects.filter(phone_number=req.data['phone_number']):
        raise CheckException(result_code=result_code.MOBILE_PHONE_NUM_REGISTERED,
                             message=_('This phone number has been registered'))

    password_check_result = check_utils.check_password(password=req.data['password'])
    if password_check_result == check_utils.PASSWORD_LENGTH_ILLEGAL:
        raise CheckException(result_code=result_code.MOBILE_PASSWORD_LENGTH_ILLEGAL,
                             message=_('Password length is too short or too long'))
    elif password_check_result == check_utils.PASSWORD_FORMAT_ILLEGAL:
        raise CheckException(result_code=result_code.MOBILE_PASSWORD_FORMAT_ILLEGAL,
                             message=_('Illegal password format'))

    if Account.objects.filter(nickname=req.data['nickname']):
        raise CheckException(result_code=result_code.MOBILE_NICKNAME_REGISTERED,
                             message=_('This nickname has been registered'))

    if req.data['gender'] != 'M' and req.data['gender'] != 'F':
        raise CheckException(result_code=result_code.MOBILE_GENDER_ILLEGAL, message=_('Illegal gender'))
    if req.data['account_type'] != 'O' and req.data['account_type'] != 'G':
        raise CheckException(result_code=result_code.MOBILE_ACCOUNT_TYPE_INVALID, message=_('Illegal account type'))
    if not authentication.check_captcha(phone_num=req.data['phone_number'], captcha_input=req.data['captcha']):
        raise CheckException(result_code=result_code.MOBILE_PHONE_CAPTCHA_INCORRECT, message=_('Incorrect captcha'))
    new_account = Account(phone_number=req.data['phone_number'],
                          password=req.data['password'],
                          nickname=req.data['nickname'],
                          gender=req.data['gender'],
                          account_type=req.data['account_type'],
                          portrait=read_default_portrait())
    new_account.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED, message=_('Register successfully'))


@api_view(['PUT'])
def send_phone_captcha(req: Request):
    if not check_utils.check_phone_num(phone_num=req.data['phone_number']):
        raise CheckException(result_code=result_code.MOBILE_PHONE_NUM_INVALID, message=_('Invalid phone number'))
    send_result = authentication.send_captcha(phone_num=req.data['phone_number'])
    if send_result == authentication.CAPTCHA_SEND_TOO_FREQUENTLY:
        raise CheckException(result_code=result_code.MOBILE_PHONE_CAPTCHA_SEND_TOO_FREQUENTLY,
                             message=_('Sending captcha must be at at least 1 minute interval'))
    elif send_result == authentication.CAPTCHA_SEND_FAILED:
        raise CheckException(result_code=result_code.MOBILE_PHONE_CAPTCHA_SEND_FAILED,
                             message=_('Send captcha failed, please try again'))
    return view_utils.get_json_response(status=status.HTTP_201_CREATED,
                                        message=_('Send captcha successfully. It will expire after 30 mins'))


@api_view(['GET'])
def check_login(req: Request):
    token_check(req)
    return Response(status=status.HTTP_204_NO_CONTENT)
