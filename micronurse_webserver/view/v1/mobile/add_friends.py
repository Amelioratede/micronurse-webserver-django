from django.core.cache import cache
from micronurse_webserver.models import Account, Friendship
from micronurse_webserver.view.v1.mobile import publish_message
from requests import Request
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils.translation import ugettext as _
from micronurse_webserver import models
from micronurse_webserver.view import result_code
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.mobile import account

MOBILE_TOKEN_VALID_HOURS = 24


@api_view(['GET'])
def get_person(req: Request, search_id: str):
    account.get_user_basic_info_by_phone(req, search_id)


def add_friends_check(user: Account, search_user: Account):
    if user.account_type == models.ACCOUNT_TYPE_OLDER\
            and search_user.account_type == models.ACCOUNT_TYPE_OLDER:
        result_list = Friendship.objects.filter(user, search_user)
        if len(result_list) == 0:
            req_token = cache.get(user.user_id + '' + search_user.user_id)
            temp_token = cache.get(search_user.user_id + '' + user.user_id)
            if req_token is not None or temp_token is not None:
                raise CheckException(result_code=result_code.MOBILE_ADD_FRIENDS_ILLEGAL,
                                     message=_('The adding friends request has existed'), status=status.status.HTTP_400_BAD_REQUEST)
            else:
                return user.user_id + '' + search_user.user_id
        else:
            raise CheckException(result_code=result_code.MOBILE_ADD_FRIENDS_ILLEGAL, message=_('The friendship has existed'),
                                 status=status.HTTP_409_CONFLICT)
    else:
        raise CheckException(result_code=result_code.MOBILE_ADD_FRIENDS_ILLEGAL, message=_('Can not build the friendship'),
                             status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def add_friends_req(req: Request):
    user_id = req.data['user_id']
    search_id = req.data['search_id']
    try:
        user = Account.objects.filter(user_id=int(user_id)).get()
        search_user = Account.objects.filter(user_id=int(search_id)).get()
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_USER_INFO_NOT_FOUND, message=_('User does not exist'),
                             status=status.HTTP_404_NOT_FOUND)
    req_id = add_friends_check(user, search_user)
    cache.set(req_id, req_id, MOBILE_TOKEN_VALID_HOURS * 3600)
    publish_message. push_adding_friends_req_message(user, search_user)
    return view_utils.get_json_response(message=_('Adding friends request has sent'), user_id=user_id, search_id=search_id)


@api_view(['PUT'])
def add_friends_resp(req: Request):
    user_id = req.data['user_id']
    adding_id = req.data['adding_id']
    adding_tag = req.data['adding_tag']
    try:
        user = Account.objects.filter(user_id=int(user_id)).get()
        adding_user = Account.objects.filter(user_id=int(adding_id)).get()
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_USER_INFO_NOT_FOUND, message=_('User does not exist'),
                             status=status.HTTP_404_NOT_FOUND)
    cache_token = cache.get(adding_id + user_id)
    if adding_tag == 'accept':
        if cache_token is not None:
            friendship = Friendship(user, adding_user)
            friendship.save()
            publish_message.push_adding_friends_resp_message(adding_tag, user_id, adding_id)
            return view_utils.get_json_response(message=_('The friendship has been built successfully'), user_id=user_id, adding_id=adding_id)
        else:
            raise CheckException(result_code=result_code.MOBILE_ADD_FRIENDS_REQUEST_INVALID, message=_('Adding friends request invalid'),
                                 status=status.HTTP_408_REQUEST_TIMEOUT)
    elif adding_tag == 'refuse':
        if cache_token is not None:
            publish_message.push_adding_friends_resp_message(adding_tag, user_id, adding_id)
            return view_utils.get_json_response(message=_('You have refused the adding friends request'), user_id=user_id, adding_id=adding_id)
        else:
            raise CheckException(result_code=result_code.MOBILE_ADD_FRIENDS_REQUEST_INVALID, message=_('Adding friends request invalid'),
                                 status=status.HTTP_408_REQUEST_TIMEOUT)
    else:
        raise CheckException(result_code=result_code.MOBILE_ADD_FRIENDS_ILLEGAL, message=_('Return Info error'),
                             status=status.HTTP_404_NOT_FOUND)

