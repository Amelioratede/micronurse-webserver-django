import time
import json
from django.core import signing
from django.core.cache import cache

from micronurse_webserver.view import result_code


def get_token(user_id: str):
    value = signing.dumps({'phone_number': str(user_id)}, salt='Micro Nurse')
    return value


def parse_token(token: str):
    origin_data = signing.loads(token, salt='Micro Nurse')
    return origin_data['phone_number']


CAPTCHA_VALID_SECOND = 1800
CAPTCHA_SEND_INTERVAL_SECOND = 60
CACHE_KEY_CAPTCHA_PREFIX = 'phone_captcha_'
CAPTCHA_SEND_TOO_FREQUENTLY = 1
CAPTCHA_SEND_FAILED = 2


def send_captcha(phone_num: str):
    origin_captcha = cache.get(CACHE_KEY_CAPTCHA_PREFIX + phone_num)
    if origin_captcha:
        origin_captcha = json.loads(origin_captcha)
        if int(time.time()) - origin_captcha['timestamp'] < CAPTCHA_SEND_INTERVAL_SECOND:
            return CAPTCHA_SEND_TOO_FREQUENTLY
    captcha = {'captcha_code': '123456', 'timestamp': int(time.time())}
    cache.set(CACHE_KEY_CAPTCHA_PREFIX + phone_num, json.dumps(captcha), CAPTCHA_VALID_SECOND)
    return result_code.SUCCESS


def check_captcha(phone_num: str, captcha_input: str):
    origin_captcha = cache.get(CACHE_KEY_CAPTCHA_PREFIX + phone_num)
    if not origin_captcha:
        return False
    origin_captcha = json.loads(origin_captcha)
    return captcha_input == origin_captcha['captcha_code']


def clear_captcha(phone_num: str):
    cache.delete(CACHE_KEY_CAPTCHA_PREFIX + phone_num)
