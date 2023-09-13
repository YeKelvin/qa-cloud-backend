#!/usr/bin/ python3
# @File    : pubilc_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
from datetime import datetime

import jwt

from flask import request
from loguru import logger

from app.extension import socketio
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserPassword
from app.tools import localvars
from app.tools.auth import JWTAuth
from app.tools.cache import executing_pymeters


@socketio.on('connect')
def connect():
    """socket连接"""
    logger.info(f'socketid:[ {request.sid} ] namespace:[ {request.namespace} ] event:[ connect ]')
    # check_login()


@socketio.on('disconnect')
def disconnect():
    """socket关闭"""
    logger.info(f'socketid:[ {request.sid} ] namespace:[ {request.namespace} ] event:[ disconnect ]')
    if running := executing_pymeters.get('request.sid'):
        stop_event = running.get('stop_event')
        stop_event.set()


@socketio.on_error_default
def error_default(e):
    """Handles all namespaces"""
    logger.error(f'socketid:[ {request.sid} ] namespace:[ {request.namespace} ] event:[ error ]\n{e}')


def check_login():
    """登录校验"""
    user_no = None
    issued_at = None
    # 校验access-token
    if 'access-token' not in request.headers:
        logger.info(f'socketid:[ {request.sid} ] 请求头缺失access-token')
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
        localvars.set('user_no', user_no)
    except jwt.ExpiredSignatureError:
        logger.info(f'socketid:[ {request.sid} ] token已失效')
        socketio.disconnect()
        return
    except jwt.InvalidTokenError:
        logger.info(f'socketid:[ {request.sid} ] 无效的token')
        socketio.disconnect()
        return
    except Exception:
        logger.exception(f'socketid:[ {request.sid} ]')
        socketio.disconnect()
        return

    # 用户不存在
    user = TUser.filter_by(USER_NO=user_no).first()
    if not user:
        logger.info(f'socketid:[ {request.sid} ] 用户不存在')
        socketio.disconnect()
        return

    # 用户未登录，请先登录
    if not user.LOGGED_IN:
        logger.info(f'socketid:[ {request.sid} ] 用户未登录')
        socketio.disconnect()
        return

    # 用户状态异常
    if user.STATE != 'ENABLE':
        logger.info(f'socketid:[ {request.sid} ] 用户状态异常')
        socketio.disconnect()
        return

    # 用户最后成功登录时间和 token 签发时间不一致，即 token 已失效
    user_password = TUserPassword.filter_by(USER_NO=user_no, PASSWORD_TYPE='LOGIN').first()
    if datetime.fromtimestamp(issued_at) != user_password.LAST_SUCCESS_TIME:
        logger.info(f'socketid:[ {request.sid} ] token已失效')
        socketio.disconnect()
        return

    localvars.set('operator', user.USER_NAME)
