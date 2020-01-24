import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from weixin import Weixin

from saleor.account.models import User

logger = logging.getLogger(__name__)

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
    return "欢迎订阅我的公众号"


def create_weixin_user(openid, user_info):
    raise NotImplementedError


def authorize_weixin_user(openid, user_info):
    email = f'{openid}@weixin.auth'
    try:
        user = User.objects.get_by_natural_key(email)
        user.is_active = True
        user.private_meta = user_info
        user.save()
    except User.DoesNotExist:
        user = create_weixin_user(openid, user_info)
    return user


@csrf_exempt
def weixin_authorize(request):
    logger.info(f'##### GET={dict(request.GET)} POST={dict(request.POST)}')
    code = request.GET.get("code")
    next = request.GET.get("next") or '/'
    data = weixin.access_token(code)
    openid = data.get('openid')
    access_token = data.get('access_token')
    from pprint import pprint
    pprint(data)
    # {'access_token': '29_2JWyReUY3SWy2FWGHyyxFCAGNajok4eVHkYr5Rr-_b9qkhjhiG5Q-cMdpa6bPpFbKOGDphSVmFOMb8OZwi6nWQ',
    #  'errcode': {},
    #  'expires_in': 7200,
    #  'openid': 'o4vCet0gGGRzWyyQK421Vdt8d67Y',
    #  'refresh_token': '29_PBZRj5lvk7kIwMRlXoQAdzTL1f4Pfssb4yTLxJeoadvFLqTP-hRUK_hY-hw0JgL6L8acATnziu85H5cmfXGG2w',
    #  'scope': 'snsapi_userinfo'}
    user_info = weixin.userinfo(access_token, openid)
    pprint(user_info)
    # {'city': '',
    #  'country': '澳大利亚',
    #  'errcode': {},
    #  'headimgurl': 'http://thirdwx.qlogo.cn/mmopen/vi_32/ajNVdqHZLLApDVEnXToNtLC2HxoUMoFdQ4EMsMicva3Ol8K9rFUjv9ianXicx3gm1QFHFFYC3obdft73RviaX4F1vQ/132',
    #  'language': 'en',
    #  'nickname': '罗韬',
    #  'openid': 'o4vCet0gGGRzWyyQK421Vdt8d67Y',
    #  'privilege': [],
    #  'province': '维多利亚',
    #  'sex': 1}
    user = authorize_weixin_user(openid, user_info)
    login(request, user)

    expiry = datetime.now() + timedelta(days=1)
    response = HttpResponseRedirect(next)
    response.set_cookie('openid', openid)
    response.set_cookie('expiry', expiry)
    return response


@csrf_exempt
def weixin_login(request):
    logger.info(f'##### GET={dict(request.GET)} POST={dict(request.POST)}')
    openid = request.GET.get("openid")
    next = request.GET.get("next")
    if openid and next:
        return redirect(next)

    callback_url = reverse('weixin:authorize')
    callback = callback_url
    url = weixin.authorize(callback, "snsapi_userinfo")
    return redirect(url)
