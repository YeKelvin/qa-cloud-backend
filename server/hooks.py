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

from server.system.model import TActionLog
from server.user.auth import Auth
from server.user.model import TUser, TPermission
from server.utils import randoms
from server.utils.log_util import get_logger

log = get_logger(__name__)


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
            log.debug('解析 Authorization HTTP Header有误')
            return
        auth_schema = auth_array[0]
        auth_token = auth_array[1]
        if auth_schema != 'JWT':
            log.debug('Authorization中的 schema请使用 JWT开头')
            return
        try:
            # 解密 token获取 payload
            payload = Auth.decode_auth_token(auth_token)
            # 设置全局属性
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


def record_action():
    """after_request

    记录请求日志，只记录成功的请求
    """
    success = getattr(g, 'success', None)
    if success:
        middle_index = request.path.index('/', 1)
        module = request.path[:middle_index]
        endpoint = request.path[middle_index:]
        permission = TPermission.query.filter_by(module=module, endpoint=endpoint).first()
        TActionLog.create(
            action_detail=permission.permission_name if permission else None,
            action_path=f'{request.method} {request.path}',
            created_time=datetime.now(),
            created_by=getattr(g, 'operator', None),
        )
