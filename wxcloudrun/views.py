import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters

logger = logging.getLogger('log')

"""below added by yang"""
import hashlib
import xml.etree.ElementTree as ET
import time
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# 你之前已有的聊天逻辑
def get_chatbot_response(msg):
    if "你好" in msg:
        return "你好，有什么可以帮您？"
    return "暂时不理解您的意思～"


# 服务号消息处理入口
@csrf_exempt
def chatbot_gzh_view(request):
    if request.method == 'GET':
        # 用于验证服务器配置（微信会发起 GET 请求进行验证）
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echostr = request.GET.get('echostr', '')

        # 获取公众号后台配置的 Token
        # 不再在代码中配置 Token，微信会自动使用公众号后台配置的 Token 进行验证

        # 将参数排序后进行 SHA1 签名并与 signature 对比
        token = ""  # 留空，微信自动使用公众号后台的 Token
        s = ''.join(sorted([token, timestamp, nonce]))
        if hashlib.sha1(s.encode()).hexdigest() == signature:
            return HttpResponse(echostr)  # 如果验证通过，返回 echostr
        else:
            return HttpResponse("验证失败")  # 如果验证失败

    elif request.method == 'POST':
        # 接收微信服务器发送的 XML 消息
        xml_data = request.body
        xml_tree = ET.fromstring(xml_data)

        # 获取发送者、接收者和消息内容
        from_user = xml_tree.find("FromUserName").text
        to_user = xml_tree.find("ToUserName").text
        content = xml_tree.find("Content").text

        # 获取聊天机器人的回复
        reply_content = get_chatbot_response(content)

        # 构建回复的 XML 数据
        reply_xml = f"""
<xml>
  <ToUserName><![CDATA[{from_user}]]></ToUserName>
  <FromUserName><![CDATA[{to_user}]]></FromUserName>
  <CreateTime>{int(time.time())}</CreateTime>
  <MsgType><![CDATA[text]]></MsgType>
  <Content><![CDATA[{reply_content}]]></Content>
</xml>
"""
        return HttpResponse(reply_xml, content_type="text/xml")  # 返回 XML 格式的回复


"""above added by yang"""

def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'index.html')


def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """

    try:
        data = Counters.objects.get(id=1)
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    return JsonResponse({'code': 0, 'data': data.count},
                        json_dumps_params={'ensure_ascii': False})


def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if 'action' not in body:
        return JsonResponse({'code': -1, 'errorMsg': '缺少action参数'},
                            json_dumps_params={'ensure_ascii': False})

    if body['action'] == 'inc':
        try:
            data = Counters.objects.get(id=1)
        except Counters.DoesNotExist:
            data = Counters()
        data.id = 1
        data.count += 1
        data.save()
        return JsonResponse({'code': 0, "data": data.count},
                    json_dumps_params={'ensure_ascii': False})
    elif body['action'] == 'clear':
        try:
            data = Counters.objects.get(id=1)
            data.delete()
        except Counters.DoesNotExist:
            logger.info('record not exist')
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': -1, 'errorMsg': 'action参数错误'},
                    json_dumps_params={'ensure_ascii': False})
