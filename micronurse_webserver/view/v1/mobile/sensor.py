from rest_framework.decorators import api_view
from rest_framework.request import Request
from django.utils.translation import ugettext as _
from micronurse import settings
from micronurse_webserver import models
from micronurse_webserver.models import Account
from micronurse_webserver.view import result_code
from micronurse_webserver.view import sensor_type as sensor
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.mobile import account


def get_sensor_json_data(sensor_data: models.Sensor):
    result = {'timestamp': int(sensor_data.timestamp.timestamp() * 1000)}
    if isinstance(sensor_data, models.Thermometer):
        result.update({'name': sensor_data.name, 'temperature': sensor_data.temperature})
    elif isinstance(sensor_data, models.Humidometer):
        result.update({'name': sensor_data.name, 'humidity': sensor_data.humidity})
    elif isinstance(sensor_data, models.SmokeTransducer):
        result.update({'name': sensor_data.name, 'smoke': sensor_data.smoke})
    elif isinstance(sensor_data, models.FeverThermometer):
        result.update({'temperature': sensor_data.temperature})
    elif isinstance(sensor_data, models.PulseTransducer):
        result.update({'pulse': sensor_data.pulse})
    elif isinstance(sensor_data, models.Turgoscope):
        result.update({'low_blood_pressure': sensor_data.low_blood_pressure,
                       'high_blood_pressure': sensor_data.high_blood_pressure})
    elif isinstance(sensor_data, models.GPS):
        result.update({'longitude': sensor_data.longitude,
                       'latitude': sensor_data.latitude})
    return result


def get_sensor_data(user: Account, sensor_type: str, limit_num:int, name: str=None):
    result_list = list()
    if sensor_type == sensor.THERMOMETER:
        if name:
            for r in models.Thermometer.objects.filter(account=user, name=name)[:limit_num]:
                result_list.append(get_sensor_json_data(sensor_data=r))
        else:
            for q in models.Thermometer.objects.raw(
                                    'SELECT * FROM ' + settings.APP_NAME + '_thermometer WHERE account_id=%s GROUP BY name',
                    [user.phone_number]):
                for r in models.Thermometer.objects.filter(account=user, name=q.name)[:limit_num]:
                    result_list.append(get_sensor_json_data(sensor_data=r))
    elif sensor_type == sensor.HUMIDOMETER:
        if name:
            for r in models.Humidometer.objects.filter(account=user, name=name)[:limit_num]:
                result_list.append(get_sensor_json_data(sensor_data=r))
        else:
            for q in models.Humidometer.objects.raw(
                                    'SELECT * FROM ' + settings.APP_NAME + '_humidometer WHERE account_id=%s GROUP BY name',
                    [user.phone_number]):
                for r in models.Humidometer.objects.filter(account=user, name=q.name)[:limit_num]:
                    result_list.append(get_sensor_json_data(sensor_data=r))
    elif sensor_type == sensor.SMOKE_TRANSDUCER:
        if name:
            for r in models.SmokeTransducer.objects.filter(account=user, name=name)[:limit_num]:
                    result_list.append(get_sensor_json_data(sensor_data=r))
        else:
            for q in models.SmokeTransducer.objects.raw(
                                    'SELECT * FROM ' + settings.APP_NAME + '_smoketransducer WHERE account_id=%s GROUP BY name',
                    [user.phone_number]):
                for r in models.SmokeTransducer.objects.filter(account=user, name=q.name)[:limit_num]:
                    result_list.append(get_sensor_json_data(sensor_data=r))
    elif sensor_type == sensor.FEVER_THERMOMETER:
        for r in models.FeverThermometer.objects.filter(account=user)[:limit_num]:
            result_list.append(get_sensor_json_data(sensor_data=r))
    elif sensor_type == sensor.PULSE_TRANSDUCER:
        for r in models.PulseTransducer.objects.filter(account=user)[:limit_num]:
            result_list.append(get_sensor_json_data(sensor_data=r))
    elif sensor_type == sensor.TURGOSCOPE:
        for r in models.Turgoscope.objects.filter(account=user)[:limit_num]:
            result_list.append(get_sensor_json_data(sensor_data=r))
    elif sensor_type == sensor.GPS:
        for r in models.GPS.objects.filter(account=user)[:limit_num]:
            result_list.append(get_sensor_json_data(sensor_data=r))
    else:
        raise CheckException(result_code=result_code.MOBILE_SENSOR_TYPE_UNSUPPORTED,
                             message=_('Unsupported sensor type'))

    if len(result_list) == 0:
        raise CheckException(result_code=result_code.MOBILE_SENSOR_DATA_NOT_FOUND,
                             message=_('Sensor data not found'))
    else:
        return view_utils.get_json_response(data_list=result_list)


@api_view(['GET'])
def get_sensor_data_older(req: Request, sensor_type: str, limit_num: int):
    user = account.token_check(req)
    return get_sensor_data(user=user, sensor_type=sensor_type.lower(), limit_num=int(limit_num))


@api_view(['GET'])
def get_sensor_data_guardian(req: Request, older_id: str, sensor_type: str, limit_num: int):
    user = account.token_check(req)
    older = Account(phone_number=older_id)
    account.guardianship_check(older=older, guardian=user)
    return get_sensor_data(user=older, sensor_type=sensor_type.lower(), limit_num=int(limit_num))


@api_view(['GET'])
def get_sensor_data_older_by_name(req: Request, sensor_type: str, name: str, limit_num: int):
    user = account.token_check(req)
    return get_sensor_data(user=user, sensor_type=sensor_type.lower(), limit_num=int(limit_num), name=name)
