import hashlib
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from weixin import Weixin

from saleor.weixin.auth import CheckSign
from saleor.weixin.autoreply import autorely

logger = logging.getLogger(__name__)



@csrf_exempt
def check_signature(request):
    if request.method == 'GET':
        logger.debug(f'[CHECK_SIGNATURE] GET={dict(request.GET)}')
        echostr = request.GET.get('echostr')

        if CheckSign(request):
            return HttpResponse(echostr)  # 必须返回echostr
        else:
            return HttpResponse('vaild signature')  # 可根据实际需要返回
    elif request.method == "POST":
        logger.debug(f'[CHECK_SIGNATURE] POST={dict(request.POST)}')
        if not CheckSign(request):
            HttpResponse('vaild signature')
        Res = autorely(request).encode('utf-8')
        return HttpResponse(Res, content_type="text/xml")


config = dict(WEIXIN_APP_ID=settings.WEIXIN_APP_ID,
              WEIXIN_TOKEN=settings.WEIXIN_APP_TOKEN,
              WEIXIN_APP_SECRET=settings.WEIXIN_APP_SECRET)
weixin = Weixin(config)

@weixin.all
def all(**kwargs):
    """
    监听所有没有更特殊的事件
    """
    return weixin.reply(kwargs['sender'], sender=kwargs['receiver'], content='all')


@weixin.text()
def hello(**kwargs):
    """
    监听所有文本消息
    """
    return "hello too"


@weixin.text("help")
def world(**kwargs):
    """
    监听help消息
    """
    return dict(content="hello world!")


@weixin.subscribe
def subscribe(**kwargs):
    """
    监听订阅消息
    """
    print(kwargs)
    return "欢迎订阅我们的公众号"
