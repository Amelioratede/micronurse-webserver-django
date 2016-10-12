import datetime
from django.http import JsonResponse
from micronurse_webserver import models
from micronurse_webserver.view import sensor_type as sensor


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
        sensor_type = sensor.THERMOMETER
    elif isinstance(sensor_data, models.Humidometer):
        sensor_type = sensor.HUMIDOMETER
    elif isinstance(sensor_data, models.SmokeTransducer):
        sensor_type = sensor.SMOKE_TRANSDUCER
    elif isinstance(sensor_data, models.InfraredTransducer):
        sensor_type = sensor.INFRARED_TRANSDUCER
    elif isinstance(sensor_data, models.FeverThermometer):
        sensor_type = sensor.FEVER_THERMOMETER
    elif isinstance(sensor_data, models.PulseTransducer):
        sensor_type = sensor.PULSE_TRANSDUCER
    elif isinstance(sensor_data, models.Turgoscope):
        sensor_type = sensor.TURGOSCOPE
    elif isinstance(sensor_data, models.GPS):
        sensor_type = sensor.GPS

    return {'sensor_type': sensor_type, 'sensor_data': get_sensor_json_data(sensor_data)}
