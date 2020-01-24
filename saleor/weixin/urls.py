from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import weixin

urlpatterns = [
    url(r'^$', csrf_exempt(weixin.django_view_func()), name='index'),

    # login entry /login/weixinmp/
]
