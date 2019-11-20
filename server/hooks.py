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

from server.user.auth import Auth
from server.user.model import TUser
from server.utils import randoms
from server.utils.log_util import get_logger

log = get_logger(__name__)


def set_user():
    """before_request

    设置单次请求的全局 user信息
    """
    if 'Authorization' in request.headers:
        auth_header = request.headers.get('Authorization')
        auth_array = auth_header.split(' ')
        if not auth_array or len(auth_array) != 2:
            log.debug('解析 Authorization HTTP Header有误')
            return
        auth_schema = auth_array[0]
        auth_token = auth_array[1]
        if auth_schema != 'JWT':
            log.debug('Authorization中的 schema属性请使用 JWT')
            return
        try:
            payload = Auth.decode_auth_token(auth_token)
            g.user = TUser.query.filter_by(user_no=payload['data']['id']).first()
            g.auth_token = auth_token
            g.auth_login_time = payload['data']['loginTime']
        except jwt.ExpiredSignatureError:
            log.debug('token 已失效')
        except jwt.InvalidTokenError:
            log.debug('无效的token')
        except Exception:
            log.error(traceback.format_exc())


def set_logid():
    """before_request

    设置单次请求的全局 logid
    """
    g.logid = (f'{threading.current_thread().ident}_'
               f'{datetime.now().strftime("%Y%m%d%H%M%S%f")}_'
               f'{randoms.get_number(4)}')


def after_request():
    log.info('after_request')


def teardown_request():
    log.info('teardown_request')


def error_handler():
    log.info('error_handler')
    return '404'
