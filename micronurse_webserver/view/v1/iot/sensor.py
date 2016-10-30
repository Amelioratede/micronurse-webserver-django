import datetime
import json
import traceback
from json import JSONDecodeError
from django.utils.translation import ugettext as _
from paho.mqtt.client import MQTTMessage
import paho.mqtt.client as mqtt_client
from micronurse_webserver.utils import mqtt_broker_utils
from django.core.cache import cache

TOPIC_SENSOR_DATA_REPORT = 'sensor_data_report'
TOPIC_SENSOR_DATA_WARNING = 'sensor_warning'

CACHE_KEY_SUPPRESS_WARNING_PREFIX = 'suppress_warning'
SUPPRESS_WARNING_MINUTES = 5

def mqtt_sensor_data_report(client: mqtt_client.Client, userdata: dict, message: MQTTMessage):
    # TODO: Push warnings for all sensor types.
    from micronurse_webserver import models
    from micronurse_webserver.utils import check_utils
    user_id = mqtt_broker_utils.parse_topic_user(str(message.topic))
    if user_id is None:
        return
    user = models.Account(phone_number=user_id)
    try:
        payload = json.loads(bytes(message.payload).decode())
    except JSONDecodeError:
        traceback.print_exc()
        return

    try:
        timestamp = datetime.datetime.fromtimestamp(int(int(payload['timestamp']) / 1000))
        value = str(payload['value'])
        name = None
        if 'name' in payload.keys():
            name = str(payload['name'])
        sensor_type = str(payload['sensor_type']).lower()
        if sensor_type == models.Humidometer.sensor_type:
            humidometer = models.Humidometer(account=user, timestamp=timestamp, name=name, humidity=float(value))
            humidometer.save()
            if check_utils.check_abnormal_sensor_value(sensor_data=humidometer):
                push_monitor_warning(older=user, sensor_data=humidometer)
            else:
                reset_suppress_warning(older=user, sensor_type=models.Humidometer.sensor_type)
        elif sensor_type == models.Thermometer.sensor_type:
            thermometer = models.Thermometer(account=user, timestamp=timestamp, name=name, temperature=float(value))
            thermometer.save()
            if check_utils.check_abnormal_sensor_value(sensor_data=thermometer):
                push_monitor_warning(older=user, sensor_data=thermometer)
            else:
                reset_suppress_warning(older=user, sensor_type=models.Thermometer.sensor_type)
        elif sensor_type == models.InfraredTransducer.sensor_type:
            if value.lower() == 'warning':
                infrared_transducer = models.InfraredTransducer(account=user, timestamp=timestamp, name=name,
                                                                warning=True)
                infrared_transducer.save()
                push_monitor_warning(older=user, sensor_data=infrared_transducer)
        elif sensor_type == models.SmokeTransducer.sensor_type:
            smoke_transducer = models.SmokeTransducer(account=user, timestamp=timestamp, name=name,
                                                      smoke=int(value))
            smoke_transducer.save()
            if check_utils.check_abnormal_sensor_value(sensor_data=smoke_transducer):
                push_monitor_warning(older=user, sensor_data=smoke_transducer)
            else:
                reset_suppress_warning(older=user, sensor_type=models.SmokeTransducer.sensor_type)
        elif sensor_type == models.GPS.sensor_type:
            location = value.split(sep=',')
            if len(location) != 2:
                return
            else:
                gps = models.GPS(account=user, timestamp=timestamp, longitude=float(location[0]),
                                 latitude=float(location[1]))
                gps.save()
        elif sensor_type == models.FeverThermometer.sensor_type:
            fever_thermometer = models.FeverThermometer(account=user, timestamp=timestamp, temperature=float(value))
            fever_thermometer.save()
            if check_utils.check_abnormal_sensor_value(sensor_data=fever_thermometer):
                push_monitor_warning(older=user, sensor_data=fever_thermometer)
            else:
                reset_suppress_warning(older=user, sensor_type=models.FeverThermometer.sensor_type)
        elif sensor_type == models.PulseTransducer.sensor_type:
            pulse_transducer = models.PulseTransducer(account=user, timestamp=timestamp, pulse=int(value))
            pulse_transducer.save()
            if check_utils.check_abnormal_sensor_value(sensor_data=pulse_transducer):
                push_monitor_warning(older=user, sensor_data=pulse_transducer)
            else:
                reset_suppress_warning(older=user, sensor_type=models.PulseTransducer.sensor_type)
        elif sensor_type == models.Turgoscope.sensor_type:
            blood_pressure = value.split(sep='/')
            if len(blood_pressure) == 2:
                turgoscope = models.Turgoscope(account=user, timestamp=timestamp,
                                               low_blood_pressure=int(blood_pressure[0]),
                                               high_blood_pressure=int(blood_pressure[1]))
                turgoscope.save()
                if check_utils.check_abnormal_sensor_value(sensor_data=turgoscope):
                    push_monitor_warning(older=user, sensor_data=turgoscope)
                else:
                    reset_suppress_warning(older=user, sensor_type=models.Turgoscope.sensor_type)
    except Exception:
        traceback.print_exc()
        return


def reset_suppress_warning(older, sensor_type: str):
    """
     :type older: micronurse_webserver.models.Account
    """
    cache_key = CACHE_KEY_SUPPRESS_WARNING_PREFIX + '/' + older.phone_number + '/' + sensor_type
    cache.delete(cache_key)


def push_monitor_warning(older, sensor_data):
    """
    :type sensor_data: micronurse_webserver.models.Sensor
    :type older: micronurse_webserver.models.Account
    """
    # TODO: Support warning messages for all sensor types.
    from micronurse_webserver import models
    if not isinstance(sensor_data, models.InfraredTransducer):
        cache_key = CACHE_KEY_SUPPRESS_WARNING_PREFIX + '/' + older.phone_number + '/' + sensor_data.sensor_type
        if cache.get(cache_key):
            return
        cache.set(cache_key, True, SUPPRESS_WARNING_MINUTES * 60)

    if isinstance(sensor_data,
                  (models.Humidometer, models.Thermometer, models.InfraredTransducer, models.SmokeTransducer)):
        msg = _('%s occur warning!') % sensor_data.name
    if isinstance(sensor_data, models.FeverThermometer):
        msg = _('Abnormal body temperature!')
    if isinstance(sensor_data, models.PulseTransducer):
        msg = _('Abnormal pulse!')
    if isinstance(sensor_data, models.Turgoscope):
        msg = _('Abnormal blood pressure!')
    mqtt_broker_utils.publish_message(topic=TOPIC_SENSOR_DATA_WARNING, topic_user=older, message=msg, qos=1)
