from django.conf.urls import url
from .views import check_signature

urlpatterns = [
    url(r"^auth/check_signature/", check_signature, name='check_signature'),
]
