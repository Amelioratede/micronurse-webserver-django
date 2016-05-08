from django.http import HttpRequest
from micronurse_webserver.models import Account
from micronurse_webserver import utils


LOGIN_SUCCESS = 0
LOGIN_USER_NOT_EXISTS = 101
LOGIN_PASSWORD_INCORRECT = 102

def iot_login(req: HttpRequest):
    req_data = utils.post_check(req)
    try:
        account = Account.objects.filter(phone_number=req_data['phone_number']).get()
        if not account.password == req_data['password']:
            return utils.get_json_response(LOGIN_PASSWORD_INCORRECT, 'Password incorrect')
        req.session['user'] = account.phone_number
        return utils.get_json_response(LOGIN_SUCCESS, 'Login Success')
    except Account.DoesNotExist:
        return utils.get_json_response(LOGIN_USER_NOT_EXISTS, 'User not exists')