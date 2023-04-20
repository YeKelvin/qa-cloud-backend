#!/usr/bin/ python3
# @File    : hook.py
# @Time    : 2019/11/7 20:02
# @Author  : Kelvin.Ye
import jwt
from flask import g
from flask import request
from loguru import logger

from app.extension import db
from app.modules.system.model import TSystemOperationLog
from app.tools import localvars
from app.tools.auth import JWTAuth
from app.tools.identity import new_ulid
from app.tools.response import http_response


def inject_traceid():
    """注入当前traceid"""
    trace_id = getattr(g, 'trace_id', None)
    if not trace_id:
        g.trace_id = new_ulid()


def inject_user():
    """注入当前user"""
    # 排除指定的请求
    if ('/user/login' in request.path) and ('POST' in request.method):
        return

    # 判断请求头部是否包含Authorization属性
    if 'Authorization' in request.headers:
        access_toekn = request.headers.get('Authorization')
        # noinspection PyBroadException
        try:
            # 解析token，获取payload
            payload = JWTAuth.decode_token(access_toekn)
            # 设置用户信息
            localvars.set('user_no', payload['data']['id'])
            localvars.set('issued_at', payload['iat'])
        except jwt.ExpiredSignatureError:
            logger.bind(traceid=g.trace_id).info(f'access-token:[ {access_toekn} ] token已失效')
        except jwt.InvalidTokenError:
            logger.bind(traceid=g.trace_id).info(f'access-token:[ {access_toekn} ] 无效的token')
        except Exception:
            logger.bind(traceid=g.trace_id).exception()


def record_operation_log():
    # 过滤无需记录的操作
    if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE'] or '/execute' in request.path:
        return
    # 记录操作日志
    oplog = TSystemOperationLog()
    oplog.LOG_NO = g.trace_id,
    oplog.OPERATION_SOURCE = 'HTTP'
    oplog.OPERATION_METHOD = request.method,
    oplog.OPERATION_ENDPOINT = request.path
    db.session.add(oplog)
    db.session.flush()


def cross_domain_access(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
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
    return http_response(errorMsg='服务器开小差')
