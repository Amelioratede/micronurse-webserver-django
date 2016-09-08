import threading
from time import sleep
import datetime
import jpush
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


def get_jpush(*push_user):
    _jpush = jpush.JPush('4a96d3acfa279d3fab851940', '163e6805a0bd57b2b7e31b1c')
    _jpush.set_logging('DEBUG')
    push = _jpush.create_push()
    push.platform = jpush.all_
    if push_user is None or len(push_user) == 0:
        push.audience = jpush.all_
    else:
        push.audience = jpush.audience(
            jpush.alias(*push_user)
        )
    return push


def task_jpush_send(push: jpush.Push, max_retry: int):
    for i in range(int(max_retry) + 1):
        try:
            push.send()
            return
        except jpush.JPushFailure as e:
            print(e.error)
            if int(e.error_code) == 1011:   # No push target
                return
        finally:
            sleep(10)


def jpush_send(push: jpush.Push, max_retry: int = 5):
    task = threading.Thread(target=task_jpush_send, args=(push, max_retry))
    task.setDaemon(True)
    task.start()


def jpush_notification_msg(push_user: list, android_msg, ios_msg=None, max_retry: int = 5):
    push = get_jpush(*push_user)
    push.notification = jpush.notification(android=android_msg, ios=ios_msg)
    jpush_send(push, max_retry=max_retry)


def get_jpush_android_notification_msg(alert_msg: str, title: str = 'Micro Nurse', extras: dict = None,
                                       builder_id: int = 1):
    return jpush.android(title=title, alert=alert_msg, builder_id=builder_id, extras=extras)


def jpush_app_msg(push_user: list, content: str, title='Micro Nurse', extra: dict = None, max_retry: int = 5):
    push = get_jpush(*push_user)
    push.message = jpush.message(content_type='application/json', title=title,
                                 msg_content=content, extras=extra)
    jpush_send(push, max_retry=max_retry)


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
