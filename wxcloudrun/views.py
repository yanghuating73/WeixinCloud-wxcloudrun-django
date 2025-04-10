import json
import logging
import time
from django.http import JsonResponse
from django.shortcuts import render

import os
import openpyxl

logger = logging.getLogger('log')
# Load the Excel table once and keep it in memory (optional optimization)
EXCEL_PATH = '/data/rules.xlsx'




# load the table to memory
# table, jurisdictions, info_types, default_message, warning_message = load_table(EXCEL_PATH)


def fuzzy_match(text, options):
    for option in options:
        if option and option.lower() in text.lower():
            return option
    return None


def test(request):
    if request.method == 'GET' or request.method == 'get':
        return JsonResponse({'code': 0, 'msg': 'ok'}, json_dumps_params={'ensure_ascii': False})
    try:
        # 2. 获取请求内容
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)  # 转换为JSON格式
        logger.info('解析后的消息内容：{}'.format(body))
    except Exception as e:
        logger.error('解析请求失败: {}'.format(str(e)))
        return JsonResponse({'code': -1, 'errorMsg': 'JSON解析失败'}, json_dumps_params={'ensure_ascii': False})

    default_message = "testing"
    reply = default_message
    # 3. 从请求中获取消息内容
    user_msg = body.get('Content', '')  # 用户输入的消息
    from_user = body.get('FromUserName', '')  # 用户的公众号ID
    to_user = body.get('ToUserName', '')  # 公众号ID


#    if not user_msg:
#        reply = default_message
#    else:
#        matched_jurisdiction = fuzzy_match(usr_msg, jurisdictions)
#        if not matched_jurisdiction:
#            reply = default_message
#        else:
#            matched_info = fuzzy_match(usr_msg, info_types)
#            if not matched_info:
#                reply = default_message
#            else:
#                result = table[matched_jurisdiction][matched_info]
#                reply = warning_message + "\n" + matched_info + ":\n" + result

    # 5. 构建回复格式
    rsp = JsonResponse({
            "ToUserName": from_user,
            "FromUserName": to_user,
            "CreateTime": int(time.time()),
            "MsgType": "text",
            "Content": reply,
    }, json_dumps_params={'ensure_ascii': False})

    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp
