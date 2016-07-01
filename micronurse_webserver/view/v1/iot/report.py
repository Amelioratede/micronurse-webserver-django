import datetime

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from micronurse_webserver import utils
from micronurse_webserver.view.v1.iot import account
from micronurse_webserver.serializer import result_code
from micronurse_webserver import utils
from micronurse_webserver import models


@api_view(['POST'])
def report(request: Request):
    user = account.token_check(request)
    print(request.body)
    timestamp = datetime.datetime.fromtimestamp(int(int(request.data['timestamp']) / 1000))
    value = str(request.data['value'])
    name = str(request.data['name'])
    sensor_type = str(request.data['sensor_type']).lower()
    if sensor_type == 'humidometer':
        humidometer = models.Humidometer(account=user, timestamp=timestamp, name=name, humidity=float(value))
        humidometer.save()
    elif sensor_type == 'thermometer':
        thermometer = models.Thermometer(account=user, timestamp=timestamp, name=name, temperature=float(value))
        thermometer.save()
    return utils.get_json_response(result_code=result_code.SUCCESS, message='Report Successfully', status=status.HTTP_201_CREATED)
