import datetime
import json
import traceback
from json import JSONDecodeError
from django.utils.translation import ugettext as _
from paho.mqtt.client import MQTTMessage
import paho.mqtt.client as mqtt_client
from micronurse_webserver.utils import mqtt_broker_utils
from micronurse_webserver.view import sensor_type as sensor


TOPIC_SENSOR_DATA_REPORT = 'sensor_data_report'
TOPIC_SENSOR_DATA_WARNING = 'sensor_warning'


def mqtt_sensor_data_report(client: mqtt_client.Client, userdata: dict, message: MQTTMessage):
    # TODO: Push warnings for all sensor types.
    from micronurse_webserver import models
    user_id = mqtt_broker_utils.parse_topic_user(str(message.topic))
    if user_id is None:
        return
    user = models.Account(phone_number=user_id)
    try:
        payload = json.loads(bytes(message.payload).decode())
    except JSONDecodeError:
        traceback.print_exc()
        return

    timestamp = datetime.datetime.fromtimestamp(int(int(payload['timestamp']) / 1000))
    value = str(payload['value'])
    name = str(payload['name'])
    sensor_type = str(payload['sensor_type']).lower()
    if sensor_type == sensor.HUMIDOMETER:
        if float(value) >= 0.9 or float(value) <= 0.1:
            humidometer = models.Humidometer(account=user, timestamp=timestamp, name=name, humidity=float(value))
            humidometer.save()
            push_monitor_warning(older=user, sensor_data=humidometer)
    elif sensor_type == sensor.THERMOMETER:
        if float(value) >= 54.0:
            thermometer = models.Thermometer(account=user, timestamp=timestamp, name=name, temperature=float(value))
            thermometer.save()
            push_monitor_warning(older=user, sensor_data= thermometer)
    elif sensor_type == sensor.INFRARED_TRANSDUCER:
        if value.lower() == 'warning':
            infrared_transducer = models.InfraredTransducer(account=user, timestamp=timestamp, name=name, warning=True)
            infrared_transducer.save()
            push_monitor_warning(older=user, sensor_data=infrared_transducer)
    elif sensor_type == sensor.SMOKE_TRANSDUCER:
        if int(value) >= 300:
            smoke_transducer = models.SmokeTransducer(account=user, timestamp=timestamp, name=name, smoke=int(value))
            smoke_transducer.save()
            push_monitor_warning(older=user, sensor_data=smoke_transducer)
    elif sensor_type == sensor.GPS:
        location = value.split(sep=',')
        if len(location) != 2:
            return
        else:
            gps = models.GPS(account=user, timestamp=timestamp, longitude=float(location[0]),
                             latitude=float(location[1]))
            gps.save()
    elif sensor_type == sensor.FEVER_THERMOMETER:
        if float(value) <= 35.5 or float(value) >= 38.0:
            fever_thermometer = models.FeverThermometer(account=user, timestamp=timestamp, temperature=float(value))
            fever_thermometer.save()
            push_monitor_warning(older=user, sensor_data=fever_thermometer)
    elif sensor_type == sensor.PULSE_TRANSDUCER:
        if int(value) >= 110 or int(value) <= 45:
            pulse_transducer = models.PulseTransducer(account=user, timestamp=timestamp, pulse=int(value))
            pulse_transducer.save()
            push_monitor_warning(older=user, sensor_data=pulse_transducer)
    elif sensor_type == sensor.TURGOSCOPE:
        blood_pressure = value.split(sep='/')
        if len(blood_pressure) == 2:
            if (int(blood_pressure[0]) <= 60 or int(blood_pressure[0]) >= 95) and (int(blood_pressure[1]) <= 90 or
                 int(blood_pressure[1]) >= 160):
                turgoscope = models.Turgoscope(account=user, timestamp=timestamp, low_blood_pressure=int(blood_pressure[0]),
                                               high_blood_pressure=int(blood_pressure[1]))
                turgoscope.save()
                push_monitor_warning(older=user, sensor_data=turgoscope)


def push_monitor_warning(older, sensor_data):
    """
    :type sensor_data: micronurse_webserver.models.Sensor
    :type older: micronurse_webserver.models.Account3
    """
    # TODO: Support warning messages for all sensor types.
    from micronurse_webserver import models
    if isinstance(sensor_data, (models.Humidometer, models.Thermometer, models.InfraredTransducer,models.SmokeTransducer)):
        msg = _('%s occur warning!') % sensor_data.name
    if isinstance(sensor_data, models.FeverThermometer):
        msg = _('fever_thermometer occur warning!')
    if isinstance(sensor_data, models.PulseTransducer):
        msg = _('pulse_transducer occur warning!')
    if isinstance(sensor_data, models.Turgoscope):
        msg = _('turgoscope occur warning!')
    mqtt_broker_utils.publish_message(topic=TOPIC_SENSOR_DATA_WARNING, topic_user=older, message=msg, qos=1)
