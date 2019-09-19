from social_core.backends.qq import QQOAuth2

from ...site import AuthenticationBackends
from . import BaseBackend


class CustomQQOAuth2(BaseBackend, QQOAuth2):
    DB_NAME = AuthenticationBackends.QQ
