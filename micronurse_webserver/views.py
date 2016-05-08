from django.http import *
from django.views.decorators.csrf import csrf_exempt

def post_check(req: HttpRequest):
    if req.method == 'GET':
        raise Http404('Page not found.')
    if not req.POST['data']:
        raise Http404('No data.')

def report(request: HttpRequest):
    post_check(request)
    print('Data:' + str(request.POST['data']))
    return HttpResponse('Hello!')