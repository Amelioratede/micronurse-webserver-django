from django.utils.translation import ugettext as _
from micronurse_webserver.models import Account
from micronurse_webserver import models
from micronurse_webserver.utils import mqtt_broker_utils

MQTT_TOPIC_BINDING_REQ_MESSAGE = 'binding_request_message'
MQTT_TOPIC_ADD_FRIENDS_REQ_MESSAGE = 'add_friends_request_message'
MQTT_TOPIC_BINDING_RESP_MESSAGE = 'binding_response_message'
MQTT_TOPIC_ADD_FRIENDS_RESP_MESSAGE = 'add_friends_response_message'


def push_binding_req_message(user: Account, search_user: Account):
    if user.account_type == models.ACCOUNT_TYPE_OLDER\
            and search_user.account_type == models.ACCOUNT_TYPE_GUARDIAN:
        msg = user.user_id + '/' + search_user.user_id + '/' + _('%s wanna bind a guardian: %s') % user.user_id % search_user.user_id
    if user.account_type == models.ACCOUNT_TYPE_GUARDIAN\
            and search_user.account_type == models.ACCOUNT_TYPE_OLDER:
        msg = user.user_id + '/' + search_user.user_id + '/' + _('%s wanna bind an older: %s') % user.user_id % search_user.user_id
    mqtt_broker_utils.publish_message(topic=MQTT_TOPIC_BINDING_REQ_MESSAGE, topic_user=search_user.user_id, message=msg, qos=1)


def push_binding_resp_message(choice: str, user_id, binding_id):
    if choice == 'accept':
        msg = binding_id + '/' + user_id + '/' + _('Bind succeeded!')
    if choice == 'refuse':
        msg == binding_id + '/' + user_id + '/' + _('Bind failed!')
    mqtt_broker_utils.publish_message(topic=MQTT_TOPIC_BINDING_RESP_MESSAGE, topic_user=binding_id, message=msg, qos=1)


def push_adding_friends_req_message(user: Account, search_user: Account):
    msg = user.user_id + '/' + search_user.user_id + '/' + _('%s wanna friend %s ') % user.user_id % search_user.user_id
    mqtt_broker_utils.publish_message(topic=MQTT_TOPIC_ADD_FRIENDS_REQ_MESSAGE, topic_user=search_user.user_id, message=msg, qos=1)


def push_adding_friends_resp_message(choice: str, user_id, adding_id):
    if choice == 'accept':
        msg = adding_id + '/' + user_id + '/' + _('Adding friends succeeded!')
    if choice == 'refuse':
        msg == adding_id + '/' + user_id + '/' + _('Adding friends failed!')
    mqtt_broker_utils.publish_message(topic=MQTT_TOPIC_ADD_FRIENDS_RESP_MESSAGE, topic_user=adding_id, message=msg, qos=1)

