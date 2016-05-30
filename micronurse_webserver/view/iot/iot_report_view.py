import datetime
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from micronurse_webserver import utils
from micronurse_webserver.view.login_view import SESSION_ATTR_IOT_USER, CACHE_KEY_IOT_TOKEN, IOT_TOKEN_VALID_HOURS
from micronurse_webserver import models

@csrf_exempt
def report(request: HttpRequest):
    account = request.session[SESSION_ATTR_IOT_USER];
    data = utils.post_check(request, CACHE_KEY_IOT_TOKEN + account.phone_number, IOT_TOKEN_VALID_HOURS)
    print('Data:' + str(request.POST['data']))
    timestamp = datetime.datetime.fromtimestamp(int(data['timestamp'] / 1000))
    value = str(data['value'])
    name = str(data['name'])
    sensor_type = str(data['sensor_type']).lower()
    if sensor_type == 'humidometer':
        humidometer = models.Humidometer(account=account, timestamp=timestamp, name=name, humidity=float(value))
        humidometer.save()
    elif sensor_type == 'thermometer':
        thermometer = models.Thermometer(account=account, timestamp=timestamp, name=name, temperature=float(value))
        thermometer.save()
    return utils.get_json_response(0, "Report successfully")
