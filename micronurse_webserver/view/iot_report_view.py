from django.http import HttpRequest
from micronurse_webserver import utils

def report(request: HttpRequest):
    utils.post_check(request)
    print('Data:' + str(request.POST['data']))
    return utils.get_json_response(0, "Report successfully")