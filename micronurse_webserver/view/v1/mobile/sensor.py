import datetime

from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from micronurse_webserver import models
from micronurse_webserver.models import Account
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view import result_code
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.mobile import account


def get_sensor_data_list(user: Account, sensor_type: str, limit_num: int, start_time: None, end_time=None,
                         name: str = None):
    result_list = []
    sensor = None
    if sensor_type == models.Thermometer.sensor_type:
        sensor = models.Thermometer
    elif sensor_type == models.Humidometer.sensor_type:
        sensor = models.Humidometer
    elif sensor_type == models.SmokeTransducer.sensor_type:
        sensor = models.SmokeTransducer
    elif sensor_type == models.InfraredTransducer:
        sensor = models.InfraredTransducer

    if sensor is not None:
        if name is None:
            for instance in models.SensorInstance.objects.filter(account=user, sensor_type=sensor_type):
                for s in sensor.objects.filter(
                        view_utils.general_query_time_limit(start_time=start_time, end_time=end_time,
                                                            instance=instance))[:limit_num]:
                    result_list.append(view_utils.get_sensor_data_dict(s))
        else:
            q = models.SensorInstance.objects.filter(account=user, sensor_type=sensor_type, name=name)
            if q:
                instance = q.get()
                for s in sensor.objects.filter(
                        view_utils.general_query_time_limit(start_time=start_time, end_time=end_time,
                                                            instance=instance))[:limit_num]:
                    result_list.append(view_utils.get_sensor_data_dict(s))
        return result_list

    if sensor_type == models.FeverThermometer.sensor_type:
        sensor = models.FeverThermometer
    elif sensor_type == models.PulseTransducer.sensor_type:
        sensor = models.PulseTransducer
    elif sensor_type == models.GPS.sensor_type:
        sensor = models.GPS

    if sensor is not None:
        for s in sensor.objects.filter(view_utils.general_query_time_limit(start_time=start_time, end_time=end_time,
                                                                           account=user))[:limit_num]:
            result_list.append(view_utils.get_sensor_data_dict(s))
    else:
        raise CheckException(result_code=result_code.MOBILE_SENSOR_TYPE_UNSUPPORTED,
                             message=_('Unsupported sensor type'))
    return result_list


@api_view(['GET'])
def get_sensor_data(req: Request, sensor_type: str, limit_num: int, start_time: str = None, end_time: str = None,
                    name: str = None, older_id: str = None):
    if older_id is None:
        user = account.token_check(req=req, permission_limit=models.ACCOUNT_TYPE_OLDER)
        older = user
    else:
        user = account.token_check(req=req, permission_limit=models.ACCOUNT_TYPE_GUARDIAN)
        older = Account(user_id=int(older_id))
        account.guardianship_check(older=older, guardian=user)

    data_list = get_sensor_data_list(user=older, sensor_type=sensor_type.lower(), limit_num=int(limit_num), name=name,
                                     start_time=start_time, end_time=end_time)
    if len(data_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MOBILE_SENSOR_DATA_NOT_FOUND,
                             message=_('Sensor data not found'))
    else:
        return view_utils.get_json_response(data_list=data_list)


def get_sensor_warning_list(user: Account, limit_num: int, start_time: datetime = None, end_time: datetime = None):
    # TODO: Get warning data for all sensor types.
    result_list = []
    instance_q = Q()
    for instance in models.SensorInstance.objects.filter(account=user,
                                                         sensor_type=models.InfraredTransducer.sensor_type):
        instance_q |= Q(instance=instance)
    if not instance_q:
        return result_list
    for it in models.InfraredTransducer.objects.filter(
            view_utils.general_query_time_limit(start_time=start_time, end_time=end_time,
                                                warning=True)) \
            .filter(instance_q)[:limit_num]:
        result_list.append(view_utils.get_sensor_warning_json_data(sensor_data=it))
    return result_list


@api_view(['GET'])
def get_sensor_warning(req: Request, limit_num: str, start_time=None, end_time=None, older_id: str = None):
    if older_id is None:
        user = account.token_check(req=req, permission_limit=models.ACCOUNT_TYPE_OLDER)
        older = user
    else:
        user = account.token_check(req=req, permission_limit=models.ACCOUNT_TYPE_GUARDIAN)
        older = Account(user_id=int(older_id))
        account.guardianship_check(older=older, guardian=user)
    warning_list = get_sensor_warning_list(user=older, limit_num=int(limit_num),
                                           start_time=start_time, end_time=end_time)
    if len(warning_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MOBILE_SENSOR_WARNING_NOT_FOUND,
                             message=_('Sensor warning not found'))
    return view_utils.get_json_response(warning_list=warning_list)


@api_view(['GET'])
def get_sensor_config(req: Request):
    user = account.token_check(req=req, permission_limit=models.ACCOUNT_TYPE_OLDER)
    config = view_utils.get_sensor_config(user=user)
    return view_utils.get_json_response(config=view_utils.get_sensor_config_dict(config))


@api_view(['PUT'])
def set_sensor_config(req: Request):
    user = account.token_check(req=req, permission_limit=models.ACCOUNT_TYPE_OLDER)
    infrared_enabled = req.data['config'].get('infrared_enabled')
    config = view_utils.get_sensor_config(user=user)
    if infrared_enabled is not None:
        config.infrared_enabled = bool(infrared_enabled)
    config.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED, message=_('Modify sensor config successfully'))
