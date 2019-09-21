import hashlib

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from saleor.weixin.auth import CheckSign
from saleor.weixin.autoreply import autorely


@csrf_exempt
def check_signature(request):
    if request.method == 'GET':
        echostr = request.GET.get('echostr')

        if CheckSign(request):
            return HttpResponse(echostr)  # 必须返回echostr
        else:
            return HttpResponse('vaild signature')  # 可根据实际需要返回
    elif request.method == "POST":
        if not CheckSign(request):
            HttpResponse('vaild signature')
        Res = autorely(request).encode('utf-8')
        return HttpResponse(Res, content_type="text/xml")
