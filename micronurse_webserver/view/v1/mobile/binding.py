from django.core.cache import cache
from micronurse_webserver.view.v1.mobile import publish_message
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.mobile import account
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from micronurse_webserver.utils import view_utils
from micronurse_webserver.models import Account, Guardianship
from micronurse_webserver import models
from micronurse_webserver.view import result_code

MOBILE_TOKEN_VALID_HOURS = 24


@api_view(['GET'])
def get_person(req: Request, search_id: str):
    account.get_user_basic_info_by_phone(req, search_id)


def binding_check(user: Account, search_user: Account):
    if user.account_type == models.ACCOUNT_TYPE_OLDER\
            and search_user.account_type == models.ACCOUNT_TYPE_GUARDIAN:
        result_list = Guardianship.objects.filter(user, search_user)
        if len(result_list) == 0:
            req_token = cache.get(user.user_id + '' + search_user.user_id)
            temp_token = cache.get(search_user.user_id + '' + user.user_id)
            if req_token is not None or temp_token is not None:
                raise CheckException(result_code=result_code.MOBILE_BINDING_ILLEGAL,
                                     message=_('The binding request has existed'), status=status.HTTP_400_BAD_REQUEST)
            else:
                return user.user_id + '' + search_user.user_id
        else:
            raise CheckException(result_code=result_code.MOBILE_BINDING_ILLEGAL, message=_('The binding has existed'),
                                 status=status.HTTP_409_CONFLICT)
    elif user.account_type == models.ACCOUNT_TYPE_GUARDIAN\
            and search_user.account_type == models.ACCOUNT_TYPE_OLDER:
        result_list = Guardianship.objects.filter(user, search_user)
        if len(result_list) == 0:
            req_token = cache.get(user.user_id + '' + search_user.user_id)
            temp_token = cache.get(search_user.user_id + '' + user.user_id)
            if req_token is not None or temp_token is not None:
                raise CheckException(result_code=result_code.MOBILE_BINDING_ILLEGAL,
                                     message=_('The binding request has existed'), status=status.HTTP_400_BAD_REQUEST)
            else:
                return user.user_id + '' + search_user.user_id
        else:
            raise CheckException(result_code=result_code.MOBILE_BINDING_ILLEGAL, message=_('The binding has existed'),
                                 status=status.HTTP_409_CONFLICT)
    else:
        raise CheckException(result_code=result_code.MOBILE_BINDING_ILLEGAL, message=_('Can not build the binding'),
                             status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def binding_req(req: Request):
    user = account.token_check(req=req)
    search_id = req.data['search_id']
    try:
        search_user = Account.objects.filter(user_id=int(search_id)).get()
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_USER_INFO_NOT_FOUND, message=_('User does not exist'),
                             status=status.HTTP_404_NOT_FOUND)
    req_id = binding_check(user, search_user)
    cache.set(req_id, req_id, MOBILE_TOKEN_VALID_HOURS * 3600)
    publish_message.push_binding_req_message(user, search_user)
    return view_utils.get_json_response(message=_('Binding request has sent'), user_id=user.user_id, search_id=search_id)


@api_view(['PUT'])
def binding_resp(req: Request):
    user = account.token_check(req=req)
    binding_id = req.data['binding_id']
    binding_tag = req.data['binding_tag']
    try:
        binding_user = Account.objects.filter(user_id=int(binding_id)).get()
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_USER_INFO_NOT_FOUND, message=_('User does not exist'),
                             status=status.HTTP_404_NOT_FOUND)
    cache_token = cache.get(binding_id + user.user_id)
    if binding_tag == 'accept':
        if cache_token is not None:
            guardianship = Guardianship(user, binding_user)
            guardianship.save()
            publish_message.push_binding_resp_message(binding_tag, user.user_id, binding_id)
            return view_utils.get_json_response(message=_('The guardianship has been built successfully'), user_id=user.user_id, binding_id=binding_id)
        else:
            raise CheckException(result_code=result_code.MOBILE_BINDING_REQUEST_INVALID, message=_('Binding request invalid'),
                                 status=status.HTTP_408_REQUEST_TIMEOUT)
    elif binding_tag == 'refuse':
        if cache_token is not None:
            publish_message.push_binding_resp_message(binding_tag, user.user_id, binding_id)
            return view_utils.get_json_response(message=_('You have refused the binding request'), user_id=user.user_id, binding_id=binding_id)
        else:
            raise CheckException(result_code=result_code.MOBILE_BINDING_REQUEST_INVALID, message=_('Binding request invalid'),
                                 status=status.HTTP_408_REQUEST_TIMEOUT)
    else:
        raise CheckException(result_code=result_code.MOBILE_BINDING_ILLEGAL, message=_('Return Info error'),
                             status=status.HTTP_404_NOT_FOUND)






