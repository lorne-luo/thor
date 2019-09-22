from social_core.backends.weixin import WeixinOAuth2, WeixinOAuth2APP

from ...site import AuthenticationBackends
from . import BaseBackend


class CustomWeixinOAuth2(BaseBackend, WeixinOAuth2):
    DB_NAME = AuthenticationBackends.WEIXIN

class CustomWeixinMpOAuth2(BaseBackend, WeixinOAuth2APP):
    DB_NAME = AuthenticationBackends.WEIXINMP
    name = 'weixinmp'

