import time
import xml.etree.cElementTree as ET

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from saleor.weixin.auth import CheckSign


@csrf_exempt
def checkwx(request):
    if request.method == "GET":
        EchoStr = request.GET.get('echostr', None)  # 获取回应字符串
        return HttpResponse(EchoStr) if CheckSign(request) else HttpResponse('vaild signature')
    elif request.method == "POST":
        if CheckSign(request) == False:
            print('check not pass')
            return None
        Res = autorely(request).encode('utf-8')
        return HttpResponse(Res, content_type="text/xml")
    else:
        return HttpResponse('invaild requests')


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
