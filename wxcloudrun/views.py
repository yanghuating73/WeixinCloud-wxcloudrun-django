import json
import logging
import time

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters

"""
# added acc. to deepseek
import hashlib
import json
import time
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class WeChatCallbackView(View):

    def get(request, _):
        rsp = JsonResponse({'code': 0, 'msg': 'ok'}, json_dumps_params={'ensure_ascii': False})
        return rsp
    def post(request, _):

        try:
            # 解析JSON消息体
            msg_data = json.loads(request.body.decode('utf-8'))

            # 构造自动回复
            response_data = self._build_response(msg_data)
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON format'},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {'error': str(e)},
                status=500
            )

    def _build_response(self, msg_data):

        base_data = {
            'ToUserName': msg_data.get('FromUserName'),
            'FromUserName': msg_data.get('ToUserName'),
            'CreateTime': int(time.time()),
            'MsgType': 'text'
        }

        # 根据消息类型处理
        msg_type = msg_data.get('MsgType')

        if msg_type == 'text':
            base_data['Content'] = f"收到文本消息: {msg_data.get('Content')}"
        elif msg_type == 'event':
            base_data['Content'] = self._handle_event(msg_data)
        else:
            base_data['Content'] = "暂不支持此消息类型"

        return base_data

    def _handle_event(self, msg_data):

        event = msg_data.get('Event')
        if event == 'subscribe':
            return "感谢关注！"
        elif event == 'unsubscribe':
            return ""  # 用户取消关注不回复
        else:
            return f"收到{event}事件"

# added acc. to deepseek
"""

logger = logging.getLogger('log')


# below added by yang
def test(request, _):

    if request.method == 'GET' or request.method == 'get':
        rsp = JsonResponse({'code': 0, 'msg': 'ok'}, json_dumps_params={'ensure_ascii': False})
    elif request.method == 'POST' or request.method == 'post':
        try:
            # 2. 获取请求内容
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)  # 转换为JSON格式
            logger.info('解析后的消息内容：{}'.format(body))
        except Exception as e:
            logger.error('解析请求失败: {}'.format(str(e)))
            return JsonResponse({'code': -1, 'errorMsg': 'JSON解析失败'}, json_dumps_params={'ensure_ascii': False})

        # 3. 从请求中获取消息内容
        user_msg = body.get('Content', '')  # 用户输入的消息
        from_user = body.get('FromUserName', '')  # 用户的公众号ID
        to_user = body.get('ToUserName', '')  # 公众号ID

        if not user_msg:
            return JsonResponse({'code': 0, 'data': '未收到消息内容'}, json_dumps_params={'ensure_ascii': False})

        # 4. 简单分析消息内容并构建自动回复
        if '你好' in user_msg:
            reply = "你好！欢迎与我对话～"
        else:
            reply = f"您说的是：{user_msg}，我收到啦～"

        # 5. 构建回复格式
        rsp = JsonResponse({
            "ToUserName": from_user,
            "FromUserName": to_user,
            "CreateTime": int(time.time()),
            "MsgType": "text",
            "Content": reply,
        }, json_dumps_params={'ensure_ascii': False})
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                           json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


#  above added by yang


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

#    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
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
        data.count += 2
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
