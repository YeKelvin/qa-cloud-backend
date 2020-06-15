#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hooks.py
# @Time    : 2019/11/7 20:02
# @Author  : Kelvin.Ye
import threading
import traceback
from datetime import datetime

import jwt
from flask import request, g

from server.librarys.helpers.global_helper import Global
from server.librarys.response import http_response
from server.system.model import TActionLog
from server.user.model import TPermission
from server.user.utils.auth import Auth
from server.utils import randoms
from server.utils.log_util import get_logger

log = get_logger(__name__)


def set_logid():
    """before_request

    设置单次请求的全局 logid
    """
    g.logid = (f'{threading.current_thread().ident}_'
               f'{datetime.utcnow().strftime("%Y%m%d%H%M%S%f")}_'
               f'{randoms.get_number(4)}')


def set_user():
    """before_request

    设置单次请求的全局 user信息
    """
    # 排除指定的请求
    if '/user/login' in request.path and 'POST' in request.method:
        return

    # 判断请求头部是否含有 Authorization属性
    if 'Authorization' in request.headers:
        # 解析 JWT token并判断是否符合规范
        auth_header = request.headers.get('Authorization')
        auth_array = auth_header.split(' ')
        if not auth_array or len(auth_array) != 2:
            log.info(f'logId:[ {g.logid} ] 解析 Authorization HTTP Header有误')
            return
        auth_schema = auth_array[0]
        auth_token = auth_array[1]
        if auth_schema != 'JWT':
            log.info(f'logId:[ {g.logid} ] Authorization中的 schema请使用 JWT开头')
            return
        try:
            # 解密 token获取 payload
            payload = Auth.decode_auth_token(auth_token)
            # 设置全局属性
            # Global.set('user', TUser.query.filter_by(user_no=payload['data']['id']).first())
            Global.set('user_no', payload['data']['id'])
            Global.set('auth_token', auth_token)
            Global.set('auth_login_time', payload['data']['loginTime'])
        except jwt.ExpiredSignatureError:
            log.info(f'logId:[ {g.logid} ] token 已失效')
        except jwt.InvalidTokenError:
            log.info(f'logId:[ {g.logid} ] 无效的token')
        except Exception:
            log.error(traceback.format_exc())


def record_action(response):
    """after_request

    记录请求日志，只记录成功的非 GET请求
    """
    success = Global.success
    if success and 'GET' not in request.method:
        permission = TPermission.query.filter_by(ENDPOINT=request.path).first()
        TActionLog.create(
            ACTION_DESC=permission.PERMISSION_NAME if permission else None,
            ACTION_METHOD=request.method,
            ACTION_ENDPOINT=request.path
        )
    return response


access_control_allow_Headers = (
    'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,X-TOKEN'
)


def cross_domain_access_before():
    if request.method == 'OPTIONS':
        response = http_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = access_control_allow_Headers
        response.headers['Access-Control-Max-Age'] = 24 * 60 * 60
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
        return response


def cross_domain_access_after(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = access_control_allow_Headers
    return response


# app.register_error_handler(404, page_not_found)
def page_not_found(_):
    return http_response(errorMsg='Resource not found'), 404


# app.register_error_handler(Exception, exception_handler)
def exception_handler(ex):
    log.exception(str(ex).replace('\n', '#'))
    return http_response(errorMsg='服务开小差')
