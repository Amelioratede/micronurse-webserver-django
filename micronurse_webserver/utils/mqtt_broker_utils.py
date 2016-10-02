import threading
import time

from micronurse import settings
import paho.mqtt.client as mqtt_client

TOPIC_SENSOR_DATA_REPORT_PREFIX = 'sensor_data_report'
TOPIC_SENSOR_WARNING_PREFIX = 'sensor_warning'

USER_DATA_FIRST_CONNECT = 'first_connect'
broker_client = None


def on_broker_connect(client: mqtt_client.Client, userdata: dict, flags, rc):
    print('Connected with MQTT broker with result code ' + str(rc))
    if userdata[USER_DATA_FIRST_CONNECT]:
        if int(rc) != 0:
            raise Exception('Connect to MQTT broker failed.')
        client.user_data_set({USER_DATA_FIRST_CONNECT: False})


def connect_to_broker():
    global broker_client
    if broker_client is not None:
        return
    broker_client = mqtt_client.Client(client_id=settings.MICRONURSE_MQTT_BROKER_CLIENT_ID, clean_session=False)
    broker_client.user_data_set({USER_DATA_FIRST_CONNECT: True})
    broker_client.username_pw_set(username=settings.MICRONURSE_MQTT_BROKER_USERNAME,
                                  password=settings.MICRONURSE_MQTT_BROKER_PASSWORD)
    broker_client.on_connect = on_broker_connect
    broker_client.connect(host='micronurse-webserver', port=13883, keepalive=15)
    broker_client.loop_start()


def disconnect_from_broker():
    global broker_client
    if broker_client is None:
        return
    broker_client.disconnect()
    broker_client = None


def mqtt_subscribe(topic: str, qos: int, max_retry: int):
    global broker_client
    for i in range(max_retry + 1):
        result, mid = broker_client.subscribe(topic=topic, qos=qos)
        if result == mqtt_client.MQTT_ERR_SUCCESS:
            print('Subscribe topic <' + topic + '> successfully.')
            break
        time.sleep(1)


def subscribe_topic(topic: str, qos: int = 0, max_retry: int = 5):
    global broker_client
    if broker_client is None:
        return
    t = threading.Thread(target=mqtt_subscribe, args=(topic, qos, max_retry))
    t.setDaemon(True)
    t.start()


def add_message_callback(topic_filter: str, callback):
    global broker_client
    if broker_client is None:
        return
    broker_client.message_callback_add(sub=topic_filter, callback=callback)


def mqtt_publish(topic: str, payload: str, qos: int, retain: bool, max_retry):
    global broker_client
    for i in range(max_retry + 1):
        result, mid = broker_client.publish(topic=topic, payload=payload, qos=qos, retain=retain)
        if result == mqtt_client.MQTT_ERR_SUCCESS:
            break
        time.sleep(1)


def publish_message(topic: str, msg: str, qos: int = 0, retain: bool = False, max_retry: int = 0):
    global broker_client
    if broker_client is None:
        return
    t = threading.Thread(target=mqtt_publish, args=(topic, msg, qos, retain, max_retry))
    t.setDaemon(True)
    t.start()


def parse_topic_user(topic: str):
    split_list = topic.split(sep='/')
    if len(split_list) <= 1:
        return None
    return split_list[len(split_list) - 1]
