import redis
from django.http import JsonResponse


def get_redis():
    return redis.StrictRedis(host='localhost', port=6379)


def get_json_response(result_code: int = 0, message: str = '', status: int=200, **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j, status=status)
