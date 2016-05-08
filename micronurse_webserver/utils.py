import time
from django.http import JsonResponse, HttpRequest, Http404
import redis
import json


def post_check(req: HttpRequest):
    if req.method == 'GET':
        raise Http404('Page not found.')
    if not req.POST['data']:
        raise Http404('No data.')
    return json.loads(req.POST['data'])


def get_json_response(result_code: int = 0, message: str = '', **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j, charset='utf-8')


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
