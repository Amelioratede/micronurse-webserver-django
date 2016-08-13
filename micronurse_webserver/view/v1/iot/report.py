import datetime

from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request

from micronurse_webserver import models
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view import result_code
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.iot import account


@api_view(['POST'])
def report(request: Request):
    user = account.token_check(request)
    print(request.body)
    timestamp = datetime.datetime.fromtimestamp(int(int(request.data['timestamp']) / 1000))
    value = str(request.data['value'])
    name = str(request.data['name'])
    sensor_type = str(request.data['sensor_type']).lower()
    result = result_code.IOT_UNSUPPORTED_SENSOR_TYPE
    if sensor_type == 'humidometer':
        humidometer = models.Humidometer(account=user, timestamp=timestamp, name=name, humidity=float(value))
        humidometer.save()
        result = result_code.SUCCESS
    elif sensor_type == 'thermometer':
        thermometer = models.Thermometer(account=user, timestamp=timestamp, name=name, temperature=float(value))
        thermometer.save()
        result = result_code.SUCCESS
    elif sensor_type == 'infrared_transducer':
        if value.lower() == 'warning':
            infrared_transducer = models.InfraredTransducer(account=user, timestamp=timestamp, name=name, warning=True)
            infrared_transducer.save()
            result = result_code.SUCCESS
        else:
            result = result_code.IOT_UNSUPPORTED_SENSOR_VALUE
    elif sensor_type == 'smoke_transducer':
        smoke_transducer = models.SmokeTransducer(account=user, timestamp=timestamp, name=name, smoke=int(value))
        smoke_transducer.save()
        result = result_code.SUCCESS
    elif sensor_type == 'gps':
        location = value.split(sep=',')
        if len(location) != 2:
            result = result_code.IOT_UNSUPPORTED_SENSOR_VALUE
        else:
            gps = models.GPS(account=user, timestamp=timestamp, longitude=float(location[0]),
                             latitude=float(location[1]))
            gps.save()
            result = result_code.SUCCESS
    elif sensor_type == 'fever_thermometer':
        fever_thermometer = models.FeverThermometer(account=user, timestamp=timestamp, temperature=float(value))
        fever_thermometer.save()
        result = result_code.SUCCESS
    elif sensor_type == 'pulse_transducer':
        pulse_transducer = models.PulseTransducer(account=user, timestamp=timestamp, pulse=int(value))
        pulse_transducer.save()
        result = result_code.SUCCESS
    elif sensor_type == 'turgoscope':
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
        raise CheckException(result_code=result_code.IOT_UNSUPPORTED_SENSOR_VALUE, message=_('Unsupported sensor value'))
