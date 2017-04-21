import shortuuid

from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from micronurse_webserver.utils import mqtt_broker_utils
from micronurse_webserver.models import Account
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view import authentication, result_code
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.iot import sensor as iot_sensor_view

CACHE_KEY_IOT_TOKEN_PREFIX = 'iot_token_'
MQTT_TOPIC_IOT_ACCOUNT = 'iot_account'
IOT_ANONYMOUS_TOKEN_VALID_HOURS = 1
CACHE_KEY_IOT_ANONYMOUS_TOKEN_PREFIX = 'iot_anonymous_token_'


@api_view(['POST'])
def get_anonymous_token(req: Request):
    temp_id = str(shortuuid.uuid())
    token_str = authentication.get_token(temp_id)
    cache.set(CACHE_KEY_IOT_TOKEN_PREFIX + temp_id, token_str, IOT_ANONYMOUS_TOKEN_VALID_HOURS * 3600)
    return view_utils.get_json_response(status=status.HTTP_201_CREATED, id=temp_id, token=token_str, expire=IOT_ANONYMOUS_TOKEN_VALID_HOURS * 3600)


def check_anonymous_token(token: str):
    try:
        temp_id = authentication.parse_token(token)
    except:
        return None
    cache_token = cache.get(CACHE_KEY_IOT_TOKEN_PREFIX + str(temp_id))
    if token != cache_token:
        return None
    return temp_id


@api_view(['GET'])
def check_anonymous_status(req: Request, temp_id: str):
    anonymous_id = check_anonymous_token(str(req.META['HTTP_AUTH_TOKEN']))
    if anonymous_id is None:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    if temp_id != str(anonymous_id):
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Token does not match given ID.'))
    return view_utils.get_json_response()


def token_check(req: Request):
    try:
        token = str(req.META['HTTP_AUTH_TOKEN'])
        user_id = int(authentication.parse_token(token))
    except:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache_token = cache.get(CACHE_KEY_IOT_TOKEN_PREFIX + str(user_id))
    if token != cache_token:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    return Account(user_id=user_id)


@api_view(['GET'])
def check_login(req: Request, user_id: str):
    user = token_check(req)
    if str(user.user_id) != user_id:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Token does not match this user.'))
    mqtt_broker_utils.subscribe_topic(topic=iot_sensor_view.MQTT_TOPIC_SENSOR_DATA_REPORT, topic_user=user.user_id, qos=1)
    return view_utils.get_json_response()


@api_view(['GET'])
def get_account_info(req: Request):
    user = token_check(req)
    user = Account.objects.filter(user_id=user.user_id).get()
    return view_utils.get_json_response(user=view_utils.get_user_info_dict(user=user))
