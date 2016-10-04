import datetime
import json
import traceback
from json import JSONDecodeError

from django.utils.translation import ugettext as _
from paho.mqtt.client import MQTTMessage
import paho.mqtt.client as mqtt_client
from micronurse_webserver.utils import mqtt_broker_utils
from rest_framework import status
from micronurse_webserver.view import result_code
from micronurse_webserver.view import sensor_type as sensor
from micronurse_webserver.view.check_exception import CheckException

TOPIC_SENSOR_DATA_REPORT = 'sensor_data_report'
TOPIC_SENSOR_DATA_WARNING = 'sensor_warning'


def mqtt_sensor_data_report(client: mqtt_client.Client, userdata: dict, message: MQTTMessage):
    # TODO: Push warnings for all sensor types.
    user_id = mqtt_broker_utils.parse_topic_user(str(message.topic))
    if user_id is None:
        return
    from micronurse_webserver import models
    from micronurse_webserver.utils import view_utils
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
        humidometer = models.Humidometer(account=user, timestamp=timestamp, name=name, humidity=float(value))
        humidometer.save()
    elif sensor_type == sensor.THERMOMETER:
        thermometer = models.Thermometer(account=user, timestamp=timestamp, name=name, temperature=float(value))
        thermometer.save()
    elif sensor_type == sensor.INFRARED_TRANSDUCER:
        if value.lower() == 'warning':
            infrared_transducer = models.InfraredTransducer(account=user, timestamp=timestamp, name=name, warning=True)
            infrared_transducer.save()
            push_monitor_warning(older=user, sensor_data=infrared_transducer)
    elif sensor_type == sensor.SMOKE_TRANSDUCER:
        smoke_transducer = models.SmokeTransducer(account=user, timestamp=timestamp, name=name, smoke=int(value))
        smoke_transducer.save()
    elif sensor_type == sensor.GPS:
        location = value.split(sep=',')
        if len(location) != 2:
            result = result_code.IOT_UNSUPPORTED_SENSOR_VALUE
        else:
            gps = models.GPS(account=user, timestamp=timestamp, longitude=float(location[0]),
                             latitude=float(location[1]))
            gps.save()
    elif sensor_type == sensor.FEVER_THERMOMETER:
        fever_thermometer = models.FeverThermometer(account=user, timestamp=timestamp, temperature=float(value))
        fever_thermometer.save()
    elif sensor_type == sensor.PULSE_TRANSDUCER:
        pulse_transducer = models.PulseTransducer(account=user, timestamp=timestamp, pulse=int(value))
        pulse_transducer.save()
    elif sensor_type == sensor.TURGOSCOPE:
        blood_pressure = value.split(sep='/')
        if len(blood_pressure) == 2:
            turgoscope = models.Turgoscope(account=user, timestamp=timestamp, low_blood_pressure=int(blood_pressure[0]),
                                           high_blood_pressure=int(blood_pressure[1]))
            turgoscope.save()


def push_monitor_warning(older, sensor_data):
    """
    :type sensor_data: micronurse_webserver.models.Sensor
    :type older: micronurse_webserver.models.Account
    """
    from micronurse_webserver import models
    # TODO: Support warning messages for all sensor types.
    if isinstance(sensor_data, models.InfraredTransducer):
        msg = _('%s occur warning!') % sensor_data.name
    mqtt_broker_utils.publish_message(topic=TOPIC_SENSOR_DATA_WARNING, topic_user=older, message=msg)
