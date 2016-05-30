import time
from django.http import JsonResponse, HttpRequest, Http404
from django.core.signing import TimestampSigner
from django.core.cache import cache
import redis
import json
import hashlib
import random


TIMESTAMP_VALID_SECONDS = 30
def post_check(req: HttpRequest, token_key: str=None, token_valid_hours: int=None):
    """
    :rtype: dict
    """
    if req.method == 'GET':
        raise Http404('Page not found.')
    if 'data' not in req.POST.keys():
        print('No data')
        raise Http404('No data.')
    if 'timestamp' not in req.POST.keys():
        print('No timestamp')
        raise Http404('No timestamp.')
    if time.time() - int(req.POST['timestamp']) > TIMESTAMP_VALID_SECONDS * 1000:
        print('URL expired.')
        raise Http404('URL expired.')
    if 'sign' not in req.POST.keys():
        print('No sign.')
        raise Http404('No sign.')
    md5_check = hashlib.md5()
    md5_check.update(req.POST['data'].encode())
    md5_check.update(req.POST['timestamp'].encode())
    token_str = None
    if not token_key == None:
        token_str = cache.get(token_key)
        if token_str == None:
            raise Http404('No token.')
        md5_check.update(token_str.encode())
    if not md5_check.hexdigest().lower() == str(req.POST['sign']).lower():
        print('md5:' + md5_check.hexdigest().lower() + ' sign:' + str(req.POST['sign']).lower())
        print('Data invalid.')
        raise Http404('Data invalid.')
    if not token_str == None:
        cache.set(token_key, token_str, token_valid_hours * 3600)
    return json.loads(req.POST['data'])


def get_token(user_id: str):
    signer = TimestampSigner(salt=random.random() * 1000000)
    return signer.sign(user_id)[len(user_id) + 1 :]


def get_json_response(result_code: int = 0, message: str = '', **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j)


def get_redis():
    return redis.StrictRedis(host='localhost', port=6379)


AUTH_CODE_VALID_SECOND = 1800
AUTH_CODE_SEND_INTERVAL = 60
REDIS_KEY_AUTH_CODE = 'AuthCode'

RESULT_SUCCESS = 0
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
