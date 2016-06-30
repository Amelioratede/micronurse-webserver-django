import json
import time
from django.core import signing
from micronurse_webserver.utils import get_redis


def get_token(user_id: str):
    value = signing.dumps({'phone_number': str(user_id)}, salt='Micro Nurse')
    return value

def parse_token(token: str):
    origin_data = signing.loads(token, salt='Micro Nurse')
    return origin_data['phone_number']


AUTH_CODE_VALID_SECOND = 1800
AUTH_CODE_SEND_INTERVAL = 60
REDIS_KEY_AUTH_CODE = 'AuthCode'
RESULT_AUTH_CODE_SEND_FREQUENTLY = 1
RESULT_AUTH_CODE_SEND_FAILED = 2


def send_auth_code(phone_number: str):
    try:
        r = get_redis()
        auth_code_info = json.load(r.get(REDIS_KEY_AUTH_CODE + phone_number))
        if time.time() - auth_code_info['sendtime'] < AUTH_CODE_SEND_INTERVAL * 1000:
            return RESULT_AUTH_CODE_SEND_FREQUENTLY
    except json.JSONDecodeError:
        auth_code_info = dict(sendtime=time.time(), authcode='123456')
        r.setex(REDIS_KEY_AUTH_CODE + phone_number, json.dump(auth_code_info), AUTH_CODE_VALID_SECOND)


def check_auth_code(phone_number: str, auth_code: str):
    try:
        r = get_redis()
        auth_code_info = json.load(r.get(REDIS_KEY_AUTH_CODE + phone_number))
        if auth_code['authcode'] == auth_code:
            r.delete(REDIS_KEY_AUTH_CODE + phone_number)
            return True
        return False
    except json.JSONDecodeError:
        return False