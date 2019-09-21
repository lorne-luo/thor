from social_core.backends.weibo import WeiboOAuth2

from ...site import AuthenticationBackends
from . import BaseBackend


class CustomWeiboOAuth2(BaseBackend, WeiboOAuth2):
    DB_NAME = AuthenticationBackends.WEIBO
