from django.conf import settings
from django.conf.urls import url
from weixin import Weixin

from .views import check_signature

config = dict(WEIXIN_APP_ID=settings.WEIXIN_APP_ID,
              WEIXIN_TOKEN=settings.WEIXIN_APP_TOKEN,
              WEIXIN_APP_SECRET=settings.WEIXIN_APP_SECRET)
weixin = Weixin(config)

urlpatterns = [
    url(r"^auth/check_signature/", check_signature, name='check_signature'),
    url(r'^$', weixin.django_view_func(), name='index'),

    # login entry /login/weixinmp/
]


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
