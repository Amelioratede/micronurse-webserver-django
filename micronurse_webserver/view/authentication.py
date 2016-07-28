from django.core import signing


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