import base64
import datetime
from django.http import JsonResponse
from micronurse_webserver import models


def get_json_response(result_code: int = 0, message: str = '', status: int = 200, **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j, status=status)


def get_datetime(java_timestamp: int = 0):
    if java_timestamp < 0:
        return None
    return datetime.datetime.fromtimestamp(java_timestamp / 1000)


def get_sensor_json_data(sensor_data: models.Sensor):
    result = {'timestamp': int(sensor_data.timestamp.timestamp() * 1000)}
    if isinstance(sensor_data, models.Thermometer):
        result.update({'name': sensor_data.name, 'temperature': sensor_data.temperature})
    elif isinstance(sensor_data, models.Humidometer):
        result.update({'name': sensor_data.name, 'humidity': sensor_data.humidity})
    elif isinstance(sensor_data, models.SmokeTransducer):
        result.update({'name': sensor_data.name, 'smoke': sensor_data.smoke})
    elif isinstance(sensor_data, models.InfraredTransducer):
        result.update({'name': sensor_data.name, 'warning': sensor_data.warning})
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
    elif isinstance(sensor_data, models.Turgoscope):
        sensor_type = models.Turgoscope.sensor_type
    elif isinstance(sensor_data, models.GPS):
        sensor_type = models.GPS.sensor_type

    return {'sensor_type': sensor_type, 'sensor_data': get_sensor_json_data(sensor_data)}


def get_user_info_json(user: models.Account, get_phone_num: bool=False):
    portrait_base64 = base64.b64encode(user.portrait).decode()
    result = dict(nickname=user.nickname, gender=user.gender, account_type=user.account_type,
                  portrait=portrait_base64)
    if get_phone_num:
        result.update({'phone_number': user.phone_number})
    return result


def get_moment_json(moment: models.FriendMoment):
    return {
        'user_id': moment.older_id,
        'text_content': moment.text_content,
        'timestamp': int(moment.timestamp.timestamp() * 1000)
    }
