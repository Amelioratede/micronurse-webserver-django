from micronurse_webserver.view import result_code
from micronurse_webserver import models
from geopy.distance import vincenty


def check_phone_num(phone_num: str):
    for c in phone_num:
        if '0' <= c <= '9':
            continue
        else:
            return False
    return True


PASSWORD_LENGTH_ILLEGAL = 1
PASSWORD_FORMAT_ILLEGAL = 2


def check_password(password: str):
    if len(password) < 6 or len(password) > 20:
        return PASSWORD_LENGTH_ILLEGAL
    return result_code.SUCCESS


def check_abnormal_sensor_value(sensor_data: models.Sensor):
    if isinstance(sensor_data, models.Humidometer):
        if sensor_data.humidity >= 90.0 or sensor_data.humidity <= 10.0:
            return True
    elif isinstance(sensor_data, models.Thermometer):
        if sensor_data.temperature >= 54.0:
            return True
    elif isinstance(sensor_data, models.SmokeTransducer):
        if sensor_data.smoke >= 300:
            return True
    elif isinstance(sensor_data, models.InfraredTransducer):
        if sensor_data.warning:
            return True
    elif isinstance(sensor_data, models.FeverThermometer):
        if sensor_data.temperature <= 35.5 or sensor_data.temperature >= 37.3:
            return True
    elif isinstance(sensor_data, models.PulseTransducer):
        if sensor_data.pulse <= 45 or sensor_data.pulse >= 110:
            return True
    elif isinstance(sensor_data, models.GPS):
        for ha in models.HomeAddress.objects.filter(older=sensor_data.account):
            home_addr = (ha.latitude, ha.longitude)
            current_addr = (sensor_data.latitude, sensor_data.longitude)
            if float(vincenty(home_addr, current_addr).meters) > 3000:
                return True
    return False
