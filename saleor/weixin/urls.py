from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import weixin, weixin_login, weixin_authorize

urlpatterns = [
    # url(r"^login/", weixin_login, name='login'),
    # url(r"^authorize/", weixin_authorize, name='authorize'),
    url(r'^$', csrf_exempt(weixin.django_view_func()), name='index'),

    # login entry /login/weixinmp/
]
