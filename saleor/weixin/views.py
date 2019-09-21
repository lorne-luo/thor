import hashlib

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def check_signature(request):
    if request.method == 'GET':
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        token = 'haimababa'

        hashlist = [token, timestamp, nonce]
        hashlist.sort()
        print('[token, timestamp, nonce]', hashlist)
        hashstr = ''.join([s for s in hashlist]).encode('utf-8')  # 这里必须增加encode('utf-8'),否则会报错
        print('hashstr befor sha1', hashstr)
        hashstr = hashlib.sha1(hashstr).hexdigest()
        print('hashstr sha1', hashstr)
        if hashstr == signature:
            return HttpResponse(echostr)  # 必须返回echostr
        else:
            return HttpResponse('error')  # 可根据实际需要返回
    else:
        return HttpResponse('chenggong')  # 可根据实际需要返回
