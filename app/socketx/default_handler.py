#!/usr/bin/ python3
# @File    : pubilc_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
from datetime import datetime

import jwt

from flask import g
from flask import request
from loguru import logger

from app.extension import socketio
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserPassword
from app.tools import localvars
from app.tools.auth import JWTAuth
from app.tools.service import socket_service


@socketio.on('connect')
@socket_service
def connect():
    """socket连接"""
    # 登录校验
    check_login()


@socketio.on('disconnect')
@socket_service
def disconnect():
    """socket关闭"""
    pass


@socketio.on_error_default
def error_default(e):
    """Handles all namespaces"""
    logger.exception(str(e))


def check_login():
    """登录校验"""
    user_no = None
    issued_at = None
    # 校验access-token
    if 'access-token' not in request.headers:
        logger.bind(traceid=g.trace_id).info('请求头缺失access-token')
        socketio.disconnect()
        return
    # 获取access-token
    access_toekn = request.headers.get('access-token')
    try:
        # 解析token，获取payload
        payload = JWTAuth.decode_token(access_toekn)
        user_no = payload['data']['id']
        issued_at = payload['iat']
        # 存储用户编号
        localvars.setg('user_no', user_no)
    except jwt.ExpiredSignatureError:
        logger.bind(traceid=g.trace_id).info('token已失效')
        socketio.disconnect()
        return
    except jwt.InvalidTokenError:
        logger.bind(traceid=g.trace_id).info('无效的token')
        socketio.disconnect()
        return
    except Exception:
        logger.bind(traceid=g.trace_id).exception('Exception Occurred')
        socketio.disconnect()
        return

    # 用户不存在
    user = TUser.filter_by(USER_NO=user_no).first()
    if not user:
        logger.bind(traceid=g.trace_id).info('用户不存在')
        socketio.disconnect()
        return

    # 用户未登录，请先登录
    if not user.LOGGED_IN:
        logger.bind(traceid=g.trace_id).info('用户未登录')
        socketio.disconnect()
        return

    # 用户状态异常
    if user.STATE != 'ENABLE':
        logger.bind(traceid=g.trace_id).info('用户状态异常')
        socketio.disconnect()
        return

    # 用户最后成功登录时间和 token 签发时间不一致，即 token 已失效
    user_password = TUserPassword.filter_by(USER_NO=user_no, PASSWORD_TYPE='LOGIN').first()
    if datetime.fromtimestamp(issued_at) != user_password.LAST_SUCCESS_TIME:
        logger.bind(traceid=g.trace_id).info('token已失效')
        socketio.disconnect()
        return

    localvars.setg('operator', user.USER_NAME)
