from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import check_signature, weixin

urlpatterns = [
    url(r"^auth/check_signature/", check_signature, name='check_signature'),
    url(r'^$', csrf_exempt(weixin.django_view_func()), name='index'),

    # login entry /login/weixinmp/
]
