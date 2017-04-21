from django.conf.urls import url, include
from micronurse_webserver.view.v1.iot import account as iot_account
from micronurse_webserver.view.v1.mobile import friend_juan
from micronurse_webserver.view.v1.mobile import account as mobile_account
from micronurse_webserver.view.v1.mobile import sensor

urlpatterns = [
    # IoT
    url(r'^iot/anonymous_token$', iot_account.get_anonymous_token),
    url(r'^iot/check_anonymous/(?P<temp_id>.+)$', iot_account.check_anonymous_status),
    url(r'^iot/check_login/(?P<user_id>\d+)$', iot_account.check_login),
    url(r'^iot/account_info$', iot_account.get_account_info),

    # Mobile
    url(r'^mobile/account/login$', mobile_account.login),
    url(r'^mobile/account/logout$', mobile_account.logout),
    url(r'^mobile/account/iot_login$', mobile_account.login_iot),
    url(r'^mobile/account/iot_logout', mobile_account.logout_iot),
    url(r'^mobile/account/user_basic_info/by_phone/(?P<phone_number>\d+)$',
        mobile_account.get_user_basic_info_by_phone),
    url(r'^mobile/account/register$', mobile_account.register),
    url(r'^mobile/account/send_captcha$', mobile_account.send_phone_captcha),
    url(r'^mobile/account/check_login/(?P<user_id>\d+)$', mobile_account.check_login),
    url(r'^mobile/account/reset_password$', mobile_account.reset_password),
    url(r'^mobile/account/guardianship$', mobile_account.get_guardianship),
    url(r'^mobile/account/set_home_address$', mobile_account.set_home_address),
    url(r'^mobile/account/home_address/(?P<older_id>\d+)$', mobile_account.get_home_address),
    url(r'^mobile/account/home_address$', mobile_account.get_home_address),

    url(
        r'^mobile/sensor/sensor_data/latest/by_name/(?P<older_id>\d+)/(?P<sensor_type>.+)/(?P<name>.+)/T(?P<start_time>\d+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(
        r'^mobile/sensor/sensor_data/latest/by_name/(?P<older_id>\d+)/(?P<sensor_type>.+)/(?P<name>.+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(
        r'^mobile/sensor/sensor_data/latest/by_name/(?P<sensor_type>.+)/(?P<name>.+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(
        r'^mobile/sensor/sensor_data/latest/by_name/(?P<sensor_type>.+)/(?P<name>.+)/T(?P<start_time>\d+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(
        r'^mobile/sensor/sensor_data/latest/by_name/(?P<sensor_type>.+)/(?P<name>.+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(
        r'^mobile/sensor/sensor_data/latest/by_name/(?P<sensor_type>.+)/(?P<name>.+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),

    url(
        r'^mobile/sensor/sensor_data/latest/(?P<older_id>\d+)/(?P<sensor_type>.+)/T(?P<start_time>\d+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(
        r'^mobile/sensor/sensor_data/latest/(?P<older_id>\d+)/(?P<sensor_type>.+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(r'^mobile/sensor/sensor_data/latest/(?P<older_id>\d+)/(?P<sensor_type>.+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(
        r'^mobile/sensor/sensor_data/latest/(?P<sensor_type>.+)/T(?P<start_time>\d+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(
        r'^mobile/sensor/sensor_data/latest/(?P<sensor_type>.+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),
    url(r'^mobile/sensor/sensor_data/latest/(?P<sensor_type>.+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_data),

    url(r'^mobile/sensor/warning/(?P<older_id>\d+)/T(?P<start_time>\d+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_warning),
    url(r'^mobile/sensor/warning/(?P<older_id>\d+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_warning),
    url(r'^mobile/sensor/warning/(?P<older_id>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_warning),
    url(r'^mobile/sensor/warning/T(?P<start_time>\d+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_warning),
    url(r'^mobile/sensor/warning/T(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        sensor.get_sensor_warning),
    url(r'^mobile/sensor/warning/(?P<limit_num>\d+)$',
        sensor.get_sensor_warning),

    url(r'^mobile/friend_juan/friendship', friend_juan.get_friendship),
    url(r'^mobile/friend_juan/post_moment', friend_juan.post_moment),

    url(r'^mobile/friend_juan/moment/T(?P<start_time>\d+)/T(?P<end_time>\d+)/(?P<limit_num>\d+)',
        friend_juan.get_moments),
    url(r'^mobile/friend_juan/moment/T(?P<end_time>\d+)/(?P<limit_num>\d+)', friend_juan.get_moments),
    url(r'^mobile/friend_juan/moment/(?P<limit_num>\d+)', friend_juan.get_moments),
]
