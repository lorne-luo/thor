from django.test import TestCase
from django.urls import reverse


class WeixinTest(TestCase):

    def test_check_signature(self):
        url = reverse('weixin:index')
        echostr = '18472664522550653'
        querystring = f'?signature=5d7b25309258d062b270c9eeb4e82db8ed922dbf&echostr={echostr}&timestamp=1579731304&nonce=1271726382'
        response = self.client.get(url + querystring)
        self.assertEqual(response.content.decode(), echostr)
