import datetime
import json
import traceback
from json.decoder import JSONDecodeError
from django.utils.translation import ugettext as _
from paho.mqtt.client import MQTTMessage
import paho.mqtt.client as mqtt_client
from micronurse_webserver.utils import mqtt_broker_utils
from django.core.cache import cache
from micronurse import settings
from django.db import transaction, connection

MQTT_TOPIC_SENSOR_DATA_REPORT = 'sensor_data_report'
MQTT_TOPIC_SENSOR_DATA_WARNING = 'sensor_warning'

CACHE_KEY_SUPPRESS_WARNING_PREFIX = 'suppress_warning'
CACHE_KEY_SENSOR_DATA_CACHE_PREFIX = 'sensor_data_cache'


def sensor_data_save():
    from micronurse_webserver import models
    from micronurse_webserver.utils import check_utils
    try:
        with transaction.atomic():
            for u in models.Account.objects.filter(account_type=models.ACCOUNT_TYPE_OLDER):
                cache_key = CACHE_KEY_SENSOR_DATA_CACHE_PREFIX + '/' + str(u.user_id)
                sensor_data_cache_dict = cache.get(cache_key)
                if sensor_data_cache_dict is None:
                    continue
                with transaction.atomic():
                    for key in sensor_data_cache_dict:
                        for s in sensor_data_cache_dict[key]:
                            if not check_utils.check_abnormal_sensor_value(s):
                                s.save()
                cache.delete(cache_key)
        print('Finish saving sensor data')
    except Exception:
        traceback.print_exc()
    connection.close()


def mqtt_sensor_data_report(client: mqtt_client.Client, userdata: dict, message: MQTTMessage):
    from micronurse_webserver import models
    from micronurse_webserver.utils import check_utils, view_utils
    user_id = mqtt_broker_utils.parse_topic_user(str(message.topic))
    if user_id is None:
        return
    user = models.Account(user_id=user_id)
    try:
        payload = json.loads(bytes(message.payload).decode())
    except JSONDecodeError:
        traceback.print_exc()
        return

    try:
        timestamp = datetime.datetime.fromtimestamp(int(payload['timestamp']))
        value = str(payload['value'])
        sensor_type = str(payload['sensor_type']).lower()
        instance = None
        new_instance_flag = False
        sensor_cfg = view_utils.get_sensor_config(user=user)
        if 'name' in payload.keys():
            name = str(payload['name'])
            q = models.SensorInstance.objects.filter(account=user, sensor_type=sensor_type, name=name)
            if q:
                instance = q.get()
            else:
                instance = models.SensorInstance(account=user, sensor_type=sensor_type, name=name)
                new_instance_flag = True

        sensor = None
        if sensor_type == models.Humidometer.sensor_type and 0 <= float(value) <= 100:
            if new_instance_flag:
                instance.save()
            sensor = models.Humidometer(instance_id=instance.id, timestamp=timestamp, humidity=float(value))
        elif sensor_type == models.Thermometer.sensor_type:
            if new_instance_flag:
                instance.save()
            sensor = models.Thermometer(instance_id=instance.id, timestamp=timestamp, temperature=float(value))
        elif sensor_type == models.InfraredTransducer.sensor_type:
            if value.lower() == 'warning' and sensor_cfg.infrared_enabled:
                if new_instance_flag:
                    instance.save()
                sensor = models.InfraredTransducer(instance_id=instance.id, timestamp=timestamp, warning=True)
        elif sensor_type == models.SmokeTransducer.sensor_type and int(value) >= 0:
            if new_instance_flag:
                instance.save()
            sensor = models.SmokeTransducer(instance_id=instance.id, timestamp=timestamp, smoke=int(value))
        elif sensor_type == models.GPS.sensor_type:
            location = value.split(sep=',')
            if len(location) != 3:
                return
            else:
                if not (-180 <= float(location[0]) <= 180 and -90 <= float(location[1]) <= 90):
                    return
                sensor = models.GPS(account=user, timestamp=timestamp, longitude=float(location[0]),
                                    latitude=float(location[1]), address=str(location[2]))
                if not check_utils.check_abnormal_sensor_value(sensor_data=sensor):
                    reset_suppress_warning(older=user, sensor_type=models.GPS.sensor_type)
        elif sensor_type == models.FeverThermometer.sensor_type:
            if float(value) < 33 or float(value) > 42:
                return
            sensor = models.FeverThermometer(account=user, timestamp=timestamp, temperature=float(value))
        elif sensor_type == models.PulseTransducer.sensor_type:
            if int(value) <= 0 or int(value) > 300:
                return
            sensor = models.PulseTransducer(account=user, timestamp=timestamp, pulse=int(value))

        if sensor is None:
            return
        abnormal_flag = check_utils.check_abnormal_sensor_value(sensor)
        if abnormal_flag:
            push_monitor_warning(older=user, sensor_data=sensor)
        cache_key = CACHE_KEY_SENSOR_DATA_CACHE_PREFIX + '/' + str(user_id)
        sensor_cache_dict = cache.get(cache_key)
        if sensor_cache_dict is None:
            sensor_cache_dict = {}
        sensor_cache_data_list = sensor_cache_dict.get(sensor_type)

        if sensor_cache_data_list is None:
            sensor_cache_dict[sensor_type] = [sensor]
            if abnormal_flag:
                sensor.save()
                connection.close()
        elif isinstance(sensor, models.FamilySensor):
            if new_instance_flag:
                sensor_cache_data_list.append(sensor)
            else:
                instance_find_flag = False
                for s in sensor_cache_data_list:
                    if s.instance.name == instance.name:
                        instance_find_flag = True
                        cache_abnormal_flag = check_utils.check_abnormal_sensor_value(s)
                        if cache_abnormal_flag and not abnormal_flag:
                            sensor_cache_data_list.insert(sensor_cache_data_list.index(s), sensor)
                        elif not cache_abnormal_flag:
                            sensor_cache_data_list[sensor_cache_data_list.index(s)] = sensor
                            if abnormal_flag:
                                sensor.save()
                                connection.close()
                        break
                if not instance_find_flag:
                    sensor_cache_data_list.append(sensor)
                    if abnormal_flag:
                        sensor.save()
                        connection.close()
        else:
            cache_abnormal_flag = check_utils.check_abnormal_sensor_value(sensor_cache_data_list[0])
            if cache_abnormal_flag and not abnormal_flag:
                sensor_cache_data_list.insert(0, sensor)
            elif not cache_abnormal_flag:
                sensor_cache_data_list[0] = sensor
                if abnormal_flag:
                    sensor.save()
                    connection.close()
        cache.set(cache_key, sensor_cache_dict, settings.MICRONURSE_SAVE_SENSOR_DATA_JOB['INTERVAL_MINUTES'] * 2 * 60)
    except Exception:
        traceback.print_exc()
        return


def reset_suppress_warning(older, sensor_type: str):
    """
     :type older: micronurse_webserver.models.Account
    """
    cache_key = CACHE_KEY_SUPPRESS_WARNING_PREFIX + '/' + older.user_id + '/' + sensor_type
    cache.delete(cache_key)


def push_monitor_warning(older, sensor_data):
    """
    :type sensor_data: micronurse_webserver.models.Sensor
    :type older: micronurse_webserver.models.Account
    """
    # TODO: Support warning messages for all sensor types.
    from micronurse_webserver import models
    if not isinstance(sensor_data, models.InfraredTransducer):
        cache_key = CACHE_KEY_SUPPRESS_WARNING_PREFIX + '/' + older.user_id + '/' + sensor_data.sensor_type
        if isinstance(sensor_data, models.GPS):
            warning_time = 0
            if cache.get(cache_key):
                warning_time = int(cache.get(cache_key))
                if warning_time >= settings.MICRONURSE_SENSOR_WARNING['GPS_WARNING_TIMES']:
                    return

            cache.set(cache_key, warning_time + 1, None)
        else:
            if cache.get(cache_key):
                return
            cache.set(cache_key, True, settings.MICRONURSE_SENSOR_WARNING['SUPPRESS_WARNING_MINUTES'] * 60)

    if isinstance(sensor_data, models.FamilySensor):
        msg = _('%s occur warning!') % sensor_data.instance.name
    if isinstance(sensor_data, models.FeverThermometer):
        msg = _('Abnormal body temperature!')
    if isinstance(sensor_data, models.PulseTransducer):
        msg = _('Abnormal pulse!')
    if isinstance(sensor_data, models.GPS):
        msg = _('Too far way from home!')
    mqtt_broker_utils.publish_message(topic=MQTT_TOPIC_SENSOR_DATA_WARNING, topic_user=older.user_id, message=msg,
                                      qos=1)
