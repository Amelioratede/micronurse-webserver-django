import datetime

from django.db.models import QuerySet
from django.utils.translation import ugettext as _
from rest_framework.decorators import api_view
from rest_framework.request import Request
from micronurse import settings
from micronurse_webserver import models
from micronurse_webserver.models import Account
from micronurse_webserver.utils import view_utils
from micronurse_webserver.utils.view_utils import get_sensor_json_data
from micronurse_webserver.view import result_code
from micronurse_webserver.view import sensor_type as sensor
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.mobile import account

def get_sensor_limited_query_set(sensor_type: models.Sensor, user: Account, limit_num: int = -1, start_time: datetime = None,
                            end_time: datetime = None, name: str = None):
    if isinstance(sensor_type, QuerySet):
        query_set = sensor_type.filter(account=user)
    else:
        query_set = sensor_type.objects.filter(account=user)
    if name:
        query_set = query_set.filter(name=name)
    if start_time:
        query_set = query_set.filter(timestamp__gte=start_time)
    if end_time:
        query_set = query_set.filter(timestamp__lte=end_time)
    if limit_num > 0:
        query_set = query_set[:limit_num]
    return query_set

def get_sensor_limited_data(sensor_type: models.Sensor, user: Account, limit_num: int = -1, start_time: datetime = None,
                            end_time: datetime = None, name: str = None):
    result_list = []
    query_set = get_sensor_limited_query_set(sensor_type=sensor_type, user=user, limit_num=limit_num, start_time=start_time, end_time=end_time, name=name)
    for r in query_set:
        result_list.append(get_sensor_json_data(sensor_data=r))
    return result_list


def get_sensor_data(user: Account, sensor_type: str, limit_num: int = -1, start_time: datetime = None,
                    end_time: datetime = None, name: str = None):
    result_list = []
    if sensor_type == sensor.THERMOMETER:
        if name:
            result_list = get_sensor_limited_data(sensor_type=models.Thermometer, user=user, limit_num=limit_num,
                                                  start_time=start_time, end_time=end_time, name=name)
        else:
            for q in models.Thermometer.objects.raw(
                                    'SELECT * FROM ' + settings.APP_NAME + '_thermometer WHERE account_id=%s GROUP BY name',
                    [user.phone_number]):
                result_list = get_sensor_limited_data(sensor_type=models.Thermometer, user=user, limit_num=limit_num,
                                                      start_time=start_time, end_time=end_time, name=q.name)
    elif sensor_type == sensor.HUMIDOMETER:
        if name:
            result_list = get_sensor_limited_data(sensor_type=models.Humidometer, user=user, limit_num=limit_num,
                                                  start_time=start_time, end_time=end_time, name=name)
        else:
            for q in models.Humidometer.objects.raw(
                                    'SELECT * FROM ' + settings.APP_NAME + '_humidometer WHERE account_id=%s GROUP BY name',
                    [user.phone_number]):
                result_list = get_sensor_limited_data(sensor_type=models.Humidometer, user=user, limit_num=limit_num,
                                                      start_time=start_time, end_time=end_time, name=q.name)
    elif sensor_type == sensor.SMOKE_TRANSDUCER:
        if name:
            result_list = get_sensor_limited_data(sensor_type=models.SmokeTransducer, user=user, limit_num=limit_num,
                                                  start_time=start_time, end_time=end_time, name=name)
        else:
            for q in models.SmokeTransducer.objects.raw(
                                    'SELECT * FROM ' + settings.APP_NAME + '_smoketransducer WHERE account_id=%s GROUP BY name',
                    [user.phone_number]):
                result_list = get_sensor_limited_data(sensor_type=models.SmokeTransducer, user=user,
                                                      limit_num=limit_num,
                                                      start_time=start_time, end_time=end_time, name=q.name)
    elif sensor_type == sensor.INFRARED_TRANSDUCER:
        if name:
            result_list = get_sensor_limited_data(sensor_type=models.InfraredTransducer, user=user, limit_num=limit_num,
                                                  start_time=start_time, end_time=end_time, name=name)
        else:
            for q in models.SmokeTransducer.objects.raw(
                                    'SELECT * FROM ' + settings.APP_NAME + '_infraredtransducer WHERE account_id=%s GROUP BY name',
                    [user.phone_number]):
                result_list = get_sensor_limited_data(sensor_type=models.SmokeTransducer, user=user,
                                                      limit_num=limit_num,
                                                      start_time=start_time, end_time=end_time, name=q.name)
    elif sensor_type == sensor.FEVER_THERMOMETER:
        result_list = get_sensor_limited_data(sensor_type=models.FeverThermometer, user=user, limit_num=limit_num,
                                              start_time=start_time, end_time=end_time, name=None)
    elif sensor_type == sensor.PULSE_TRANSDUCER:
        result_list = get_sensor_limited_data(sensor_type=models.PulseTransducer, user=user, limit_num=limit_num,
                                              start_time=start_time, end_time=end_time, name=None)
    elif sensor_type == sensor.TURGOSCOPE:
        result_list = get_sensor_limited_data(sensor_type=models.Turgoscope, user=user, limit_num=limit_num,
                                              start_time=start_time, end_time=end_time, name=None)
    elif sensor_type == sensor.GPS:
        result_list = get_sensor_limited_data(sensor_type=models.GPS, user=user, limit_num=limit_num,
                                              start_time=start_time, end_time=end_time, name=None)
    else:
        raise CheckException(result_code=result_code.MOBILE_SENSOR_TYPE_UNSUPPORTED,
                             message=_('Unsupported sensor type'))

    if len(result_list) == 0:
        raise CheckException(result_code=result_code.MOBILE_SENSOR_DATA_NOT_FOUND,
                             message=_('Sensor data not found'))
    else:
        return view_utils.get_json_response(data_list=result_list)


@api_view(['GET'])
def get_sensor_data_older(req: Request, sensor_type: str, limit_num: int, start_time: int = -1, end_time: int = -1,
                          name: str = None):
    user = account.token_check(req)
    return get_sensor_data(user=user, sensor_type=sensor_type.lower(), limit_num=int(limit_num), name=name,
                           start_time=view_utils.get_datetime(int(start_time)),
                           end_time=view_utils.get_datetime(int(end_time)))


@api_view(['GET'])
def get_sensor_data_guardian(req: Request, older_id: str, sensor_type: str, limit_num: int, start_time: int = -1,
                             end_time: int = -1, name: str = None):
    user = account.token_check(req)
    older = Account(phone_number=older_id)
    account.guardianship_check(older=older, guardian=user)
    return get_sensor_data(user=older, sensor_type=sensor_type.lower(), limit_num=int(limit_num), name=name,
                           start_time=view_utils.get_datetime(int(start_time)),
                           end_time=view_utils.get_datetime(int(end_time)))


def get_sensor_warning(user: Account, start_time: datetime=None, end_time: datetime=None, limit_num: int=-1):
    # TODO: Get warning data for all sensor types.
    result_list = []
    query_set = models.InfraredTransducer.objects.filter(warning=True)
    query_set = get_sensor_limited_query_set(sensor_type=query_set, user=user, start_time=start_time, end_time=end_time, limit_num=limit_num)
    for q in query_set:
        result_list.append(view_utils.get_sensor_warning_json_data(sensor_data=q))
    if len(result_list) == 0:
        raise CheckException(result_code=result_code.MOBILE_SENSOR_WARNING_NOT_FOUND,
                             message=_('Sensor warning not found'))
    return view_utils.get_json_response(warning_list=result_list)


@api_view(['GET'])
def get_sensor_warning_older(req: Request, start_time: int=-1, end_time: int=-1, limit_num: int=-1):
    user = account.token_check(req)
    return get_sensor_warning(user=user, limit_num=int(limit_num),
                              start_time=view_utils.get_datetime(int(start_time)),
                              end_time=view_utils.get_datetime(int(end_time)))


@api_view(['GET'])
def get_sensor_warning_guardian(req: Request, older_id: str, start_time: int=-1, end_time: int=-1, limit_num: int=-1):
    user = account.token_check(req)
    older = Account(phone_number=older_id)
    account.guardianship_check(older=older, guardian=user)
    return get_sensor_warning(user=older, limit_num=int(limit_num),
                              start_time=view_utils.get_datetime(int(start_time)),
                              end_time=view_utils.get_datetime(int(end_time)))

