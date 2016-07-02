from django.conf.urls import url, include
from micronurse_webserver.view.v1.iot import account as iot_account
from micronurse_webserver.view.v1.iot import report as iot_report
from micronurse_webserver.view.v1.mobile import account as mobile_account


urlpatterns = [
    #IoT
    url(r'^iot/login', iot_account.login),
    url(r'^iot/logout', iot_account.logout),
    url(r'^iot/report', iot_report.report),

    #Mobile
    url(r'^mobile/login', mobile_account.login),
    url(r'^mobile/user/by_phone/(?P<phone_number>[0-9]+)', mobile_account.get_user_basic_info_by_phone)
]