from rest_framework.decorators import api_view
from rest_framework.request import Request
from django.utils.translation import ugettext as _
from micronurse import settings
from micronurse_webserver import models
from micronurse_webserver.view import result_code
from micronurse_webserver.view import sensor_type as sensor
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.mobile import account


@api_view(['GET'])
def get_sensor_data_older(req: Request, sensor_type: str, limit_num: int):
    user = account.token_check(req)
    sensor_type = sensor_type.lower()
    result_list = list()
    result = result_code.MOBILE_SENSOR_TYPE_UNSUPPORTED
    if sensor_type == sensor.THERMOMETER:
        for q in models.Thermometer.objects.raw(
                                'SELECT * FROM ' + settings.APP_NAME + '_thermometer WHERE account_id=%s GROUP BY name',
                [user.phone_number]):
            for r in models.Thermometer.objects.filter(account=user, name=q.name)[:int(limit_num)]:
                result_list.append(
                    {'name': q.name, 'timestamp': int(r.timestamp.timestamp() * 1000), 'temperature': r.temperature})
        result = result_code.SUCCESS
    elif sensor_type == sensor.HUMIDOMETER:
        for q in models.Humidometer.objects.raw(
                                'SELECT * FROM ' + settings.APP_NAME + '_humidometer WHERE account_id=%s GROUP BY name',
                [user.phone_number]):
            for r in models.Humidometer.objects.filter(account=user, name=q.name)[:int(limit_num)]:
                result_list.append(
                    {'name': q.name, 'timestamp': int(r.timestamp.timestamp() * 1000), 'humidity': r.humidity})
        result = result_code.SUCCESS
    elif sensor_type == sensor.SMOKE_TRANSDUCER:
        for q in models.SmokeTransducer.objects.raw(
                                'SELECT * FROM ' + settings.APP_NAME + '_smoketransducer WHERE account_id=%s GROUP BY name',
                [user.phone_number]):
            for r in models.SmokeTransducer.objects.filter(account=user, name=q.name)[:int(limit_num)]:
                result_list.append(
                    {'name': q.name, 'timestamp': int(r.timestamp.timestamp() * 1000), 'smoke': r.smoke})
        result = result_code.SUCCESS

    if result == result_code.SUCCESS:
        if len(result_list) == 0:
            raise CheckException(result_code=result_code.MOBILE_SENSOR_DATA_NOT_FOUND,
                                 message=_('Sensor data not found'))
        else:
            return view_utils.get_json_response(data_list=result_list)
    elif result == result_code.MOBILE_SENSOR_TYPE_UNSUPPORTED:
        raise CheckException(result_code=result_code.MOBILE_SENSOR_TYPE_UNSUPPORTED,
                             message=_('Unsupported sensor type'))
