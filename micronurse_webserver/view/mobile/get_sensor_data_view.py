from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

from micronurse_webserver import utils, models

GET_DATA_SUCCESS = 0
GET_DATA_NO_DATA = 100;
GET_DATA_SENSOR_TYPE_ERROR = 200;


@csrf_exempt
def get_test_sensor_data(request: HttpRequest):
    account = models.Account.objects.get(phone_number='123456')
    data = utils.post_check(request)
    print('Data:' + str(request.POST['data']))
    sensor_type = str(data['sensor_type']).lower()
    name = str(data['name'])
    if sensor_type == 'humidometer':
        try:
            humidometer = models.Humidometer.objects.filter(account=account, name=name)[0]
        except IndexError:
            return utils.get_json_response(GET_DATA_NO_DATA, message='No data')
        return utils.get_json_response(GET_DATA_SUCCESS, message='Get data success',
                                       timestamp=int(humidometer.timestamp.timestamp() * 1000), humidity=humidometer.humidity)
    return utils.get_json_response(GET_DATA_SENSOR_TYPE_ERROR, 'Sensor type error')