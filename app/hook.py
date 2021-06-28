#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hook.py
# @Time    : 2019/11/7 20:02
# @Author  : Kelvin.Ye
import threading
import traceback
from datetime import datetime

import jwt
from flask import g
from flask import request

from app.common import global_variables as gvars
from app.common.response import http_response
from app.system.model import TActionLog
from app.user.model import TPermission
from app.utils import randoms
from app.utils.auth import JWTAuth
from app.utils.log_util import get_logger


log = get_logger(__name__)


def set_logid():
    """
    before_request
    设置当前请求的全局logId
    """
    g.logid = (
        f'{threading.current_thread().ident}'
        f'{datetime.utcnow().strftime("%Y%m%d%H%M%S%f")}'
        f'{randoms.get_number(4)}'
    )


def set_user():
    """
    before_request
    设置当前请求的全局user信息
    """
    # 排除指定的请求
    if ('/user/login' in request.path) and ('POST' in request.method):
        return

    # 判断请求头部是否包含Authorization属性
    if 'Authorization' in request.headers:
        # 判断Authorization是否符合规范
        auth_header = request.headers.get('Authorization')
        auth_array = auth_header.split(' ')
        if not auth_array or len(auth_array) != 2:
            log.info(f'logId:[ {g.logid} ] 解析Authorization Header有误')
            return

        auth_schema, auth_token = auth_array
        if auth_schema != 'Bearer':
            log.info(f'logId:[ {g.logid} ] 暂不支持的schema')
            return

        try:
            # 解析token，获取payload
            payload = JWTAuth.decode_auth_token(auth_token)
            # 设置全局属性
            gvars.put('user_no', payload['data']['id'])
            gvars.put('auth_token', auth_token)
            gvars.put('auth_login_time', payload['data']['loginTime'])
        except jwt.ExpiredSignatureError:
            log.info(f'logId:[ {g.logid} ] token已失效')
        except jwt.InvalidTokenError:
            log.info(f'logId:[ {g.logid} ] 无效的token')
        except Exception:
            log.error(traceback.format_exc())


def record_action(response):
    """
    after_request
    记录请求日志，只记录成功的非GET请求
    """
    success = gvars.get_success()
    if success and 'GET' not in request.method:
        permission = TPermission.query.filter_by(ENDPOINT=request.path).first()
        TActionLog.insert(
            ACTION_DESC=permission.PERMISSION_NAME if permission else None,
            ACTION_METHOD=request.method,
            ACTION_ENDPOINT=request.path
        )
    return response


access_control_allow_Headers = (
    'Accept,Accept-Encoding,Accept-Language,'
    'Access-Control-Allow-Origin,Authorization,'
    'Content-Type,Connection,Cache-Control,'
    'Host,Origin,Referer,User-Agent'
)


def cross_domain_access(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers['Access-Control-Allow-Headers'] = access_control_allow_Headers
    response.headers['Access-Control-Allow-Headers'] = '*'

    if request.method == 'OPTIONS':
        response.headers['Access-Control-Max-Age'] = 60 * 60 * 24
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE'

    return response


# app.register_error_handler(404, page_not_found)
def page_not_found(_):
    return http_response(errorMsg='Resource not found'), 404


# app.register_error_handler(Exception, exception_handler)
def exception_handler(ex):
    log.exception(str(ex).replace('\n', '#'))
    return http_response(errorMsg='服务开小差')
