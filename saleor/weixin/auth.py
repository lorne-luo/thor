import hashlib
import os

from django.conf import settings
from django.contrib.sites.models import Site

from saleor.site import AuthenticationBackends

weixin_key = Site.objects.get(id=settings.SITE_ID).settings.authorizationkey_set.filter(
    name=AuthenticationBackends.WEIXIN).first()



def CheckSign(requests):
    os.getpid()
    form = {}
    form['signature'] = requests.GET.get('signature', None)
    form['timestamp'] = requests.GET.get('timestamp', None)
    form['nonce'] = requests.GET.get('nonce', None)
    form['token'] = settings.WEIXIN_API_TOKEN
    Signature = form.pop('signature')
    Key = hashlib.sha1("".join(sorted([form[i] for i in form])).encode('utf-8')).hexdigest()  # 获得sha1加密后结果
    return True if Signature == Key else False
