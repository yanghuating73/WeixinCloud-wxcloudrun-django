import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters

logger = logging.getLogger('log')

"""below added by yang"""


def chat_gzh(request, _):
    """
    处理来自公众号的消息推送（JSON 格式）

    `` request `` 请求对象
    """

    logger.info('chat_gzh req: {}'.format(request.body))

    if request.method != 'POST':
        return JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})

    try:
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        logger.info('parsed json: {}'.format(body))
    except Exception as e:
        logger.error('解析请求失败: {}'.format(str(e)))
        return JsonResponse({'code': -1, 'errorMsg': 'JSON解析失败'},
                            json_dumps_params={'ensure_ascii': False})

    # 示例：简单回显收到的消息
    user_msg = body.get('Content', '')
    from_user = body.get('FromUserName', '')
    to_user = body.get('ToUserName', '')

    if not user_msg:
        return JsonResponse({'code': 0, 'data': '未收到消息内容'},
                            json_dumps_params={'ensure_ascii': False})

    reply = f'您说的是：{user_msg}，我收到了～'

    return JsonResponse({
        'code': 0,
        'data': {
            'to_user': from_user,
            'from_user': to_user,
            'reply': reply
        }
    }, json_dumps_params={'ensure_ascii': False})


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
