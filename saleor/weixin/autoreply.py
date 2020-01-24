import hashlib
import logging
import os
import time
import xml.etree.cElementTree as ET

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from social_core.pipeline.user import user_details

logger = logging.getLogger(__name__)


# unused code

def CheckSign(requests):
    os.getpid()
    form = {}
    form['signature'] = requests.GET.get('signature', None)
    form['timestamp'] = requests.GET.get('timestamp', None)
    form['nonce'] = requests.GET.get('nonce', None)
    form['token'] = settings.WEIXIN_APP_TOKEN
    Signature = form.pop('signature')
    Key = hashlib.sha1("".join(sorted([form[i] for i in form])).encode('utf-8')).hexdigest()  # 获得sha1加密后结果
    return True if Signature == Key else False


def custom_user_details(strategy, details, user=None, *args, **kwargs):
    """Update user details using data from provider."""

    logger.warning('details', details)
    logger.warning('user', user)
    logger.warning('args', args)
    logger.warning('kwargs', kwargs)

    return user_details(strategy, details, user=None, *args, **kwargs),


# 预留处理接口
# 推荐直接返回XML
def DealTextMsg(*args, **kwds):  # 处理文本信息
    pass


def DealImageMsg(*args, **kwds):  # 处理图片信息
    pass


def DealVoiceMsg(*args, **kwds):  # 处理声音信息
    pass


def DealVideoMsg(*args, **kwds):  # 处理视频信息
    pass


def DealShortVideoMsg(*args, **kwds):  # 处理短视频信息
    pass


XMLtemplate = '<xml> <ToUserName>< ![CDATA[%s] ]></ToUserName> <FromUserName>< ![CDATA[%s] ]></FromUserName> <CreateTime>%s</CreateTime> <MsgType>< ![CDATA[%s] ]\
        ></MsgType> <Content>< ![CDATA[%s] ]></Content> </xml>'


def CreateXML(**kwds):  # 生成返回消息的XML
    return (XMLtemplate % (
        kwds['ToUserName'], kwds['FromUserName'], kwds['CreateTime'], kwds['MsgType'], kwds['Content'])).replace(' ',
                                                                                                                 '')


def autorely(requests):
    webData = requests.body
    Root = ET.fromstring(webData)
    ToUserName = Root.find('ToUserName').text
    FromUserName = Root.find('FromUserName').text
    CreateTime = Root.find('CreateTime').text
    MsgType = Root.find('MsgType').text
    MsgId = Root.find('MsgId').text
    if MsgType == 'text':
        Content = Root.find('Content').text
        DealTextMsg(Content)
        return CreateXML(ToUserName=requests.GET['openid'], FromUserName=ToUserName, CreateTime=int(time.time()),
                         MsgType='text', Content=Content)
    elif MsgType == 'image':
        ResourceUrl = Root.find('PicUrl').text
        DealImageMsg()
        return CreateXML(ToUserName=requests.GET['openid'], FromUserName=ToUserName, CreateTime=int(time.time()),
                         MsgType='text', Content='图片已经接收\nUrl:%s' % ResourceUrl)
    elif MsgType == 'voice':
        DealVoiceMsg()
        return CreateXML(ToUserName=requests.GET['openid'], FromUserName=ToUserName, CreateTime=int(time.time()),
                         MsgType='text', Content='语音已接收到')
    elif MsgType == 'video':
        DealVideoMsg()
        return CreateXML(ToUserName=requests.GET['openid'], FromUserName=ToUserName, CreateTime=int(time.time()),
                         MsgType='text', Content='视频已接收到')
    elif MsgType == 'shortvideo':
        DealShortVideoMsg()
        return CreateXML(ToUserName=requests.GET['openid'], FromUserName=ToUserName, CreateTime=int(time.time()),
                         MsgType='text', Content='小视频已接收到')
    else:
        return CreateXML(ToUserName=requests.GET['openid'], FromUserName=ToUserName, CreateTime=int(time.time()),
                         MsgType='text', Content='不支持该数据类型')



@csrf_exempt
def check_signature(request):
    if request.method == 'GET':
        echostr = request.GET.get('echostr')

        if CheckSign(request):
            return HttpResponse(echostr)  # 必须返回echostr
        else:
            return HttpResponse('vaild signature')  # 可根据实际需要返回
    elif request.method == "POST":
        if not CheckSign(request):
            HttpResponse('vaild signature')
        Res = autorely(request).encode('utf-8')
        return HttpResponse(Res, content_type="text/xml")
