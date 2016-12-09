import os

from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from micronurse.settings import BASE_DIR
from micronurse_webserver import models
from micronurse_webserver.models import Account,HomeAddress
from micronurse_webserver.utils import view_utils, check_utils
from micronurse_webserver.view import authentication, result_code
from micronurse_webserver.view.check_exception import CheckException

CACHE_KEY_MOBILE_TOKEN_PREFIX = 'mobile_token_'
MOBILE_TOKEN_VALID_HOURS = 120


def token_check(req: Request, permission_limit: str = None):
    try:
        token = req.META['HTTP_AUTH_TOKEN']
        user_id = authentication.parse_token(token)
    except Exception:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache_token = cache.get(CACHE_KEY_MOBILE_TOKEN_PREFIX + str(user_id))
    if token != cache_token:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache.set(CACHE_KEY_MOBILE_TOKEN_PREFIX + str(user_id), cache_token, MOBILE_TOKEN_VALID_HOURS * 3600)
    if permission_limit is not None:
        user = Account.objects.filter(user_id=user_id).get()
        if user.account_type != permission_limit:
            raise CheckException(status=status.HTTP_403_FORBIDDEN, result_code=status.HTTP_403_FORBIDDEN,
                                 message=_('Permission denied'))
    else:
        user = Account(user_id=user_id)
    return user


def guardianship_check(older: Account, guardian: Account):
    try:
        models.Guardianship.objects.filter(older=older, guardian=guardian).get()
    except models.Guardianship.DoesNotExist:
        raise CheckException(status=status.HTTP_403_FORBIDDEN, result_code=result_code.MOBILE_GUARDIANSHIP_NOT_EXIST,
                             message=_('Guardianship does not exist'))


@api_view(['PUT'])
def login(request: Request):
    try:
        account = Account.objects.filter(phone_number=request.data['phone_number']).get()
        if not account.password == request.data['password']:
            raise CheckException(result_code=result_code.MOBILE_LOGIN_INCORRECT_PASSWORD,
                                 message=_('Incorrect password'), status=status.HTTP_401_UNAUTHORIZED)
        token_str = authentication.get_token(account.user_id)
        cache.set(CACHE_KEY_MOBILE_TOKEN_PREFIX + str(account.user_id), token_str, MOBILE_TOKEN_VALID_HOURS * 3600)
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
        return view_utils.get_json_response(user=view_utils.get_user_info_json(user=user))
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_USER_INFO_NOT_FOUND, message=_('User does not exist'),
                             status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_guardianship(req: Request):
    user = token_check(req=req)
    user = Account.objects.filter(user_id=user.user_id).get()
    user_list = list()
    if user.account_type == models.ACCOUNT_TYPE_OLDER:
        for g in models.Guardianship.objects.filter(older=user):
            user_list.append(view_utils.get_user_info_json(user=g.guardian, get_phone_num=True))
    elif user.account_type == models.ACCOUNT_TYPE_GUARDIAN:
        for g in models.Guardianship.objects.filter(guardian=user):
            user_list.append(view_utils.get_user_info_json(user=g.older, get_phone_num=True))

    if len(user_list) == 0:
        raise CheckException(result_code=result_code.MOBILE_GUARDIANSHIP_NOT_EXIST, message=_('Guardianship does not exist'),
                             status=status.HTTP_404_NOT_FOUND)
    return view_utils.get_json_response(user_list=user_list)


@api_view(['DELETE'])
def logout(req: Request):
    user = token_check(req=req)
    cache.delete(CACHE_KEY_MOBILE_TOKEN_PREFIX + str(user.user_id))
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


@api_view(['POST'])
def set_home_address(request:Request):
    user = token_check(req=request, permission_limit=models.ACCOUNT_TYPE_OLDER)
    user = Account.objects.filter(user_id=user.user_id).get()
    longitude = request.data['home_longitude']
    latitude = request.data['home_latitude']
    if 73.0 <= longitude <= 135.0 and 3 <= latitude <= 53:
        if user.account_type == models.ACCOUNT_TYPE_OLDER:
            new_home_address = HomeAddress(longitude=longitude,latitude=latitude,
                                           older=user)
            new_home_address.save()
            return view_utils.get_json_response(status=status.HTTP_201_CREATED,
                                                message=_("Set home address successfully"))
        if user.account_type == models.ACCOUNT_TYPE_GUARDIAN:
            raise CheckException(result_code=result_code.MOBILE_HOME_ADDRESS_SETTING_PERMISSIONS_LIMITED,
                                 message=_("Only older can set home address"))
    else:
        raise CheckException(result_code=result_code.MOBILE_HOME_ADDRESS_ILLEGAL,
                             message=_("Address is out of scope"))


@api_view(['GET'])
def get_home_address_from_older(request: Request):
    user = token_check(req=request, permission_limit=models.ACCOUNT_TYPE_OLDER)
    try:
        home_address = HomeAddress.objects.filter(older=user).get()
        longitude = home_address.longitude
        latitude = home_address.latitude
        return view_utils.get_json_response(latitude=latitude, longitude=longitude)
    except HomeAddress.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_HOME_ADDRESS_NOT_EXIST, message=_('Home address not exist'),
                             status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_home_address_from_guardian(request: Request, older_id: str):
    user = token_check(req=request, permission_limit=models.ACCOUNT_TYPE_GUARDIAN)
    older = Account(user_id=int(older_id))
    guardianship_check(guardian=user, older=older)
    try:
        home_address = HomeAddress.objects.filter(older=older).get()
        longitude = home_address.longitude
        latitude = home_address.latitude
        return view_utils.get_json_response(latitude=latitude, longitude=longitude)
    except HomeAddress.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_HOME_ADDRESS_NOT_EXIST,
                             message=_('Home address not exist'), status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def reset_password(req: Request):
    try:
        account = Account.objects.filter(phone_number=req.data['phone_number']).get()

        password_check_result = check_utils.check_password(password=req.data['new_password'])
        if password_check_result == check_utils.PASSWORD_LENGTH_ILLEGAL:
            raise CheckException(result_code=result_code.MOBILE_PASSWORD_LENGTH_ILLEGAL,
                                 message=_('Password length is too short or too long'))
        elif password_check_result == check_utils.PASSWORD_FORMAT_ILLEGAL:
            raise CheckException(result_code=result_code.MOBILE_PASSWORD_FORMAT_ILLEGAL,
                                 message=_('Illegal password format'))

        if not authentication.check_captcha(phone_num=req.data['phone_number'], captcha_input=req.data['captcha']):
            raise CheckException(result_code=result_code.MOBILE_PHONE_CAPTCHA_INCORRECT, message=_('Incorrect captcha'))

        account.password = req.data['new_password']
        account.save()
        return view_utils.get_json_response(message=_('Reset password successfully'))
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_LOGIN_USER_NOT_EXIST, message=_('User does not exist'),
                             status=status.HTTP_401_UNAUTHORIZED)


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
def check_login(req: Request, user_id: str):
    user = token_check(req=req)
    if str(user.user_id) != user_id:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Token does not match this user.'))
    return view_utils.get_json_response()
