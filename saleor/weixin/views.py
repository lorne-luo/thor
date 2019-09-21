import hashlib

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from saleor.weixin.auth import CheckSign


@csrf_exempt
def check_signature(request):
    if request.method == 'GET':
        echostr = request.GET.get('echostr')

        if CheckSign(request):
            return HttpResponse(echostr)  # 必须返回echostr
        else:
            return HttpResponse('error')  # 可根据实际需要返回
    else:
        return HttpResponse('chenggong')  # 可根据实际需要返回
