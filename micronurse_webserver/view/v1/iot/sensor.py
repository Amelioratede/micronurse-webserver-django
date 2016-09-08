import datetime
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from micronurse_webserver import models
from micronurse_webserver.view import result_code
from micronurse_webserver.view import sensor_type as sensor
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.iot import account


@api_view(['POST'])
def report(request: Request):
    # TODO: Push warnings for all sensor types.
    user = account.token_check(request)
    print(request.body)
    timestamp = datetime.datetime.fromtimestamp(int(int(request.data['timestamp']) / 1000))
    value = str(request.data['value'])
    name = str(request.data['name'])
    sensor_type = str(request.data['sensor_type']).lower()
    result = result_code.IOT_UNSUPPORTED_SENSOR_TYPE
    if sensor_type == sensor.HUMIDOMETER:
        humidometer = models.Humidometer(account=user, timestamp=timestamp, name=name, humidity=float(value))
        humidometer.save()
        result = result_code.SUCCESS
    elif sensor_type == sensor.THERMOMETER:
        thermometer = models.Thermometer(account=user, timestamp=timestamp, name=name, temperature=float(value))
        thermometer.save()
        result = result_code.SUCCESS
    elif sensor_type == sensor.INFRARED_TRANSDUCER:
        if value.lower() == 'warning':
            infrared_transducer = models.InfraredTransducer(account=user, timestamp=timestamp, name=name, warning=True)
            infrared_transducer.save()
            push_monitor_warning(older=user, sensor_data=infrared_transducer)
            result = result_code.SUCCESS
        else:
            result = result_code.IOT_UNSUPPORTED_SENSOR_VALUE
    elif sensor_type == sensor.SMOKE_TRANSDUCER:
        smoke_transducer = models.SmokeTransducer(account=user, timestamp=timestamp, name=name, smoke=int(value))
        smoke_transducer.save()
        result = result_code.SUCCESS
    elif sensor_type == sensor.GPS:
        location = value.split(sep=',')
        if len(location) != 2:
            result = result_code.IOT_UNSUPPORTED_SENSOR_VALUE
        else:
            gps = models.GPS(account=user, timestamp=timestamp, longitude=float(location[0]),
                             latitude=float(location[1]))
            gps.save()
            result = result_code.SUCCESS
    elif sensor_type == sensor.FEVER_THERMOMETER:
        fever_thermometer = models.FeverThermometer(account=user, timestamp=timestamp, temperature=float(value))
        fever_thermometer.save()
        result = result_code.SUCCESS
    elif sensor_type == sensor.PULSE_TRANSDUCER:
        pulse_transducer = models.PulseTransducer(account=user, timestamp=timestamp, pulse=int(value))
        pulse_transducer.save()
        result = result_code.SUCCESS
    elif sensor_type == sensor.TURGOSCOPE:
        blood_pressure = value.split(sep='/')
        if len(blood_pressure) != 2:
            result = result_code.IOT_UNSUPPORTED_SENSOR_VALUE
        else:
            turgoscope = models.Turgoscope(account=user, timestamp=timestamp, low_blood_pressure=int(blood_pressure[0]),
                                           high_blood_pressure=int(blood_pressure[1]))
            turgoscope.save()
            result = result_code.SUCCESS

    if result == result_code.SUCCESS:
        return view_utils.get_json_response(message=_('Report successfully'), status=status.HTTP_201_CREATED)
    elif result == result_code.IOT_UNSUPPORTED_SENSOR_TYPE:
        raise CheckException(result_code=result_code.IOT_UNSUPPORTED_SENSOR_TYPE, message=_('Unsupported sensor type'))
    elif result == result_code.IOT_UNSUPPORTED_SENSOR_VALUE:
        raise CheckException(result_code=result_code.IOT_UNSUPPORTED_SENSOR_VALUE,
                             message=_('Unsupported sensor value'))


def push_monitor_warning(older: models.Account, sensor_data: models.Sensor):
    # TODO: Support warning messages for all sensor types.
    older = models.Account.objects.filter(phone_number=older.phone_number).get()
    title = _('Monitor Warning-%s') % older.nickname
    older_content = None
    guardian_content = None
    if isinstance(sensor_data, models.InfraredTransducer):
        older_content = guardian_content = _('%s occur warning!') % sensor_data.name
    if older_content:
        view_utils.jpush_app_msg(push_user=[older.phone_number], content=older_content, title=title,
                                 extra=view_utils.get_sensor_warning_json_data(sensor_data=sensor_data))
    if guardian_content:
        guardian_list = []
        for g in models.Guardianship.objects.filter(older=older):
            guardian_list.append(g.guardian.phone_number)
        if len(guardian_list) > 0:
            view_utils.jpush_app_msg(push_user=guardian_list, content=guardian_content, title=title,
                                     extra=view_utils.get_sensor_warning_json_data(sensor_data=sensor_data))
