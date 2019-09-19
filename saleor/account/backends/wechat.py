from social_core.backends.weixin import WeixinOAuth2, WeixinOAuth2APP

from ...site import AuthenticationBackends
from . import BaseBackend


class CustomWechatOAuth2(BaseBackend, WeixinOAuth2):
    DB_NAME = AuthenticationBackends.WECHAT
