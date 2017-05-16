import signal
import sys
from django.apps import AppConfig
import django.dispatch
from micronurse_webserver.utils import mqtt_broker_utils, scheduler_utils
from micronurse_webserver.view.v1.iot.sensor import MQTT_TOPIC_SENSOR_DATA_REPORT, mqtt_sensor_data_report, sensor_data_save
from micronurse import settings


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
        scheduler_utils.init_scheduler()
        scheduler_utils.add_interval_job(job_id='job_save_sensor_data', job_func=sensor_data_save,
                                         minutes=settings.MICRONURSE_SAVE_SENSOR_DATA_JOB['INTERVAL_MINUTES'])
        signal.signal(signal.SIGINT, self.on_server_shutdown)

    def on_server_shutdown(self, signal, frame):
        mqtt_broker_utils.disconnect_from_broker()
        scheduler_utils.stop_scheduler()
        self.shutdown_signal.send('system')
        sys.exit(0)