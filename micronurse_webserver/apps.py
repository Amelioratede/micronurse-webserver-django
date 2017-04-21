import signal
import sys
from django.apps import AppConfig
import django.dispatch
from micronurse_webserver.utils import mqtt_broker_utils
from micronurse_webserver.view.v1.iot.sensor import MQTT_TOPIC_SENSOR_DATA_REPORT
from micronurse_webserver.view.v1.iot.sensor import mqtt_sensor_data_report


class MicronurseWebserverConfig(AppConfig):
    name = 'micronurse_webserver'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.shutdown_signal = django.dispatch.Signal()

    def ready(self):
        mqtt_broker_utils.init_client()
        mqtt_broker_utils.add_message_callback(topic_filter=MQTT_TOPIC_SENSOR_DATA_REPORT + '/#',
                                               callback=mqtt_sensor_data_report)
        mqtt_broker_utils.connect_to_broker()
        signal.signal(signal.SIGINT, self.on_server_shutdown)

    def on_server_shutdown(self, signal, frame):
        mqtt_broker_utils.disconnect_from_broker()
        self.shutdown_signal.send('system')
        sys.exit(0)