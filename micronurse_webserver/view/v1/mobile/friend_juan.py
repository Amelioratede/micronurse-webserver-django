import datetime
import time

from django.db.models import Q
from requests import Request
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils.translation import ugettext as _
from micronurse_webserver import models
from micronurse_webserver.view import result_code
from micronurse_webserver.utils import view_utils
from micronurse_webserver.view.check_exception import CheckException
from micronurse_webserver.view.v1.mobile import account


@api_view(['GET'])
def get_friendship(request: Request):
    user = account.token_check(req=request, permission_limit=models.ACCOUNT_TYPE_OLDER)
    user_list = list()
    if user.account_type == models.ACCOUNT_TYPE_OLDER:
        for f in models.Friendship.objects.filter(older=user):
            user_list.append(view_utils.get_user_info_json(user=f.friend, get_phone_num=False))
    if len(user_list) == 0:
        raise CheckException(result_code=result_code.MOBILE_RESULT_NOT_FOUND, message=_('Friend list is empty'),
                             status=status.HTTP_404_NOT_FOUND)
    return view_utils.get_json_response(user_list=user_list)


@api_view(['POST'])
def post_moment(req: Request):
    user = account.token_check(req=req, permission_limit=models.ACCOUNT_TYPE_OLDER)
    moment = models.FriendMoment(older=user, timestamp=datetime.datetime.fromtimestamp(time.time()),
                                 text_content=str(req.data['text_content']))
    moment.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED, message=_('Post moment successfully'))


@api_view(['GET'])
def get_moments(req: Request, start_time: int = -1, end_time: int = -1, limit_num: int = -1):
    user = account.token_check(req=req, permission_limit=models.ACCOUNT_TYPE_OLDER)
    moment_list = []
    friend_limit = Q(older=user)
    for fs in models.Friendship.objects.filter(older=user):
        friend_limit |= Q(older=fs.friend)
    moment_query_set = models.FriendMoment.objects.filter(friend_limit)
    if int(start_time) >= 0:
        moment_query_set.filter(timestamp__gte=view_utils.get_datetime(int(start_time)))
    if int(end_time) >= 0:
        moment_query_set.filter(timestamp__lte=view_utils.get_datetime(int(end_time)))
    if int(limit_num) > 0:
        moment_query_set = moment_query_set[:int(limit_num)]
    for fm in moment_query_set:
        moment_list.append(view_utils.get_moment_json(moment=fm))
    if len(moment_list) == 0:
        raise CheckException(result_code=result_code.MOBILE_FRIEND_JUAN_NO_MOMENT, message=_('No friend moment'),
                             status=status.HTTP_404_NOT_FOUND)
    return view_utils.get_json_response(moment_list=moment_list)