import json

from django.http import HttpResponse
from requests import HTTPError
from social_core.backends.weixin import WeixinOAuth2, WeixinOAuth2APP
from social_core.exceptions import AuthCanceled, AuthUnknownError

from . import BaseBackend
from ...site import AuthenticationBackends


class CustomWeixinMixin(object):
    EXTRA_DATA = [
        ('openid', 'openid'),
        ('sex', 'sex'),
        ('province', 'province'),
        ('city', 'city'),
        ('country', 'country'),
        ('privilege', 'privilege'),
        ('unionid', 'unionid'),
        ('headimgurl', 'profile_image_url'),
    ]

    def get_user_details(self, response):
        openid=response.get('openid', '')
        return {
            'email': f'{openid}@weixinmp.com',
            'first_name': response.get('nickname', ''),
            'last_name': response.get('nickname', ''),
            'profile_image_url': response.get('headimgurl', ''),
            'unionid': response.get('unionid', '')
        }


class CustomWeixinOAuth2(CustomWeixinMixin, BaseBackend, WeixinOAuth2):
    DB_NAME = AuthenticationBackends.WEIXIN
    name = AuthenticationBackends.WEIXIN


class CustomWeixinMpOAuth2(CustomWeixinMixin, BaseBackend, WeixinOAuth2APP):
    DB_NAME = AuthenticationBackends.WEIXINMP
    name = AuthenticationBackends.WEIXINMP
    DEFAULT_SCOPE = ['snsapi_userinfo']
    GET_ALL_EXTRA_DATA = True

    def auth_complete(self, *args, **kwargs):
        """Completes login process, must return user instance"""
        self.process_error(self.data)
        try:
            response = self.request_access_token(
                self.ACCESS_TOKEN_URL,
                data=self.auth_complete_params(self.validate_state()),
                headers=self.auth_headers(),
                method=self.ACCESS_TOKEN_METHOD
            )
        except HTTPError as err:
            if err.response.status_code == 400:
                raise AuthCanceled(self)
            else:
                raise
        except KeyError:
            raise AuthUnknownError(self)

        if 'errcode' in response:
            return HttpResponse(json.dumps(response))
            # raise AuthCanceled(self)
        self.process_error(response)
        return self.do_auth(response['access_token'], response=response,
                            *args, **kwargs)
