import threading
from time import sleep

import datetime
import jpush
from django.http import JsonResponse


def get_json_response(result_code: int = 0, message: str = '', status: int = 200, **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j, status=status)


def get_datetime(java_timestamp: int = 0):
    if java_timestamp < 0:
        return None
    return datetime.datetime.fromtimestamp(java_timestamp / 1000)


def get_jpush(*push_user):
    _jpush = jpush.JPush('4a96d3acfa279d3fab851940', '163e6805a0bd57b2b7e31b1c')
    _jpush.set_logging('DEBUG')
    push = _jpush.create_push()
    push.platform = jpush.all_
    if push_user is None or len(push_user) == 0:
        push.audience = jpush.all_
    else:
        push.audience = jpush.audience(
            jpush.alias(*push_user)
        )
    return push


def task_jpush_send(push: jpush.Push, max_retry: int):
    for i in range(int(max_retry) + 1):
        try:
            push.send()
            return
        except jpush.JPushFailure as e:
            print(e.error)
        finally:
            sleep(10)


def jpush_send(push: jpush.Push, max_retry: int = 5):
    task = threading.Thread(target=task_jpush_send, args=(push, max_retry))
    task.setDaemon(True)
    task.start()


def jpush_notification_msg(push_user: list, android_msg, ios_msg=None, max_retry: int = 5):
    push = get_jpush(*push_user)
    push.notification = jpush.notification(android=android_msg, ios=ios_msg)
    jpush_send(push, max_retry=max_retry)


def get_jpush_android_notification_msg(alert_msg: str, title: str = 'Micro Nurse', extras: dict = None,
                                       builder_id: int = 1):
    return jpush.android(title=title, alert=alert_msg, builder_id=builder_id, extras=extras)


def jpush_app_msg(push_user: list, content: str, title='Micro Nurse', extra: dict=None, max_retry: int = 5):
    push = get_jpush(push_user)
    push.message = jpush.message(content_type='application/json', title=title,
                                 content=content, extras=extra)
    jpush_send(push, max_retry=max_retry)
