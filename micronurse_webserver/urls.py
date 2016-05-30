"""micronurse_webserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from micronurse_webserver.view import login_view, logout_view
from micronurse_webserver.view.iot import iot_report_view
from micronurse_webserver.view.mobile import get_sensor_data_view


urlpatterns = [
    url(r'^iot/report', iot_report_view.report, name='iot/report'),
    url(r'^iot/login', login_view.iot_login, name='iot/login'),
    url(r'^iot/logout', logout_view.iot_logout, name='iot/logout'),
    url(r'^mobile/login', login_view.mobile_login, name='mobile/login'),
    url(r'^mobile/gettestsensordata', get_sensor_data_view.get_test_sensor_data, name='mobile/gettestsensordata')
]
