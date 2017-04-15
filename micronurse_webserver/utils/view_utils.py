import base64
import datetime

from django.db.models import Q
from django.http import JsonResponse
from micronurse_webserver import models


def get_json_response(result_code: int = 0, message: str = '', status: int = 200, **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j, status=status)


def get_sensor_data_dict(sensor_data: models.Sensor):
    result = {'timestamp': int(sensor_data.timestamp.timestamp())}
    if isinstance(sensor_data, models.Thermometer):
        result.update({'name': sensor_data.instance.name, 'temperature': sensor_data.temperature})
    elif isinstance(sensor_data, models.Humidometer):
        result.update({'name': sensor_data.instance.name, 'humidity': sensor_data.humidity})
    elif isinstance(sensor_data, models.SmokeTransducer):
        result.update({'name': sensor_data.instance.name, 'smoke': sensor_data.smoke})
    elif isinstance(sensor_data, models.InfraredTransducer):
        result.update({'name': sensor_data.instance.name, 'warning': sensor_data.warning})
    elif isinstance(sensor_data, models.FeverThermometer):
        result.update({'temperature': sensor_data.temperature})
    elif isinstance(sensor_data, models.PulseTransducer):
        result.update({'pulse': sensor_data.pulse})
    elif isinstance(sensor_data, models.GPS):
        result.update({'longitude': sensor_data.longitude,
                       'latitude': sensor_data.latitude,
                       'address': sensor_data.address})
    return result


def get_sensor_warning_json_data(sensor_data: models.Sensor):
    if isinstance(sensor_data, models.Thermometer):
        sensor_type = models.Thermometer.sensor_type
    elif isinstance(sensor_data, models.Humidometer):
        sensor_type = models.Humidometer.sensor_type
    elif isinstance(sensor_data, models.SmokeTransducer):
        sensor_type = models.SmokeTransducer.sensor_type
    elif isinstance(sensor_data, models.InfraredTransducer):
        sensor_type = models.InfraredTransducer.sensor_type
    elif isinstance(sensor_data, models.FeverThermometer):
        sensor_type = models.FeverThermometer.sensor_type
    elif isinstance(sensor_data, models.PulseTransducer):
        sensor_type = models.PulseTransducer.sensor_type
    elif isinstance(sensor_data, models.GPS):
        sensor_type = models.GPS.sensor_type

    return {'sensor_type': sensor_type, 'sensor_data': get_sensor_data_dict(sensor_data)}


def get_user_info_dict(user: models.Account, get_phone_num: bool=False):
    portrait_base64 = base64.b64encode(user.portrait).decode()
    result = dict(nickname=user.nickname, gender=user.gender, account_type=user.account_type,
                  portrait=portrait_base64, user_id=user.user_id)
    if get_phone_num:
        result.update({'phone_number': user.phone_number})
    return result


def get_moment_dict(moment: models.FriendMoment):
    return {
        'user_id': moment.older_id,
        'text_content': moment.text_content,
        'timestamp': int(moment.timestamp.timestamp())
    }


def general_query_time_limit(end_time=None, start_time=None, **kwargs):
    if end_time is not None:
        q = Q(timestamp__lte=datetime.datetime.fromtimestamp(int(end_time)))
    else:
        q = Q(timestamp__lte=datetime.datetime.now())
    if start_time is not None:
        q &= Q(timestamp__gte=datetime.datetime.fromtimestamp(int(start_time)))
    for k, v in kwargs.items():
        if v is not None:
            d = {k: v}
            q &= Q(**d)
    return q
