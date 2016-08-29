from django.conf.urls import url, include
from micronurse_webserver.view.v1.iot import account as iot_account
from micronurse_webserver.view.v1.iot import sensor as iot_sensor
from micronurse_webserver.view.v1.mobile import account as mobile_account
from micronurse_webserver.view.v1.mobile import sensor

urlpatterns = [
    # IoT
    url(r'^iot/login', iot_account.login),
    url(r'^iot/logout', iot_account.logout),
    url(r'^iot/report', iot_sensor.report),

    # Mobile
    url(r'^mobile/account/login', mobile_account.login),
    url(r'^mobile/account/logout', mobile_account.logout),
    url(r'^mobile/account/user_basic_info/by_phone/(?P<phone_number>[0-9]+)',
        mobile_account.get_user_basic_info_by_phone),
    url(r'^mobile/account/register', mobile_account.register),
    url(r'^mobile/account/send_captcha', mobile_account.send_phone_captcha),
    url(r'^mobile/account/check_login', mobile_account.check_login),
    url(r'^mobile/account/reset_password', mobile_account.reset_password),
    url(r'^mobile/account/guardianship', mobile_account.get_guardianship),

    url(r'^mobile/sensor/sensor_data/older/latest/(?P<sensor_type>.+)/(?P<limit_num>[0-9]+)',
        sensor.get_sensor_data_older),
    url(r'^mobile/sensor/sensor_data/guardian/latest/(?P<older_id>[0-9]+)/(?P<sensor_type>.+)/(?P<limit_num>[0-9]+)',
        sensor.get_sensor_data_guardian),
    url(r'^mobile/sensor/sensor_data/older/latest/(?P<sensor_type>.+)/(?P<name>.+)/(?P<limit_num>[0-9]+)',
        sensor.get_sensor_data_older_by_name),
]
