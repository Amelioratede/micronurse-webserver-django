from django.conf.urls import url, include
from micronurse_webserver.view.v1.iot import report, account


urlpatterns = [
    #IoT
    url(r'^iot/login', account.login),
    url(r'^iot/logout', account.logout),
    url(r'^iot/report', report.report)
]