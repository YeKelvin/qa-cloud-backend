#!/usr/bin/ python3
# @File    : hook.py
# @Time    : 2019/11/7 20:02
# @Author  : Kelvin.Ye
from flask import g
from flask import request

from app.extension import db
from app.modules.system.model import TSystemOperationLog
from app.tools.identity import new_ulid
from app.tools.response import http_response


def inject_traceid():
    """注入当前traceid"""
    trace_id = getattr(g, 'trace_id', None)
    if not trace_id:
        g.trace_id = new_ulid()


def record_operation_log():
    # 过滤无需记录的操作
    if request.method not in ['POST', 'PUT', 'DELETE']:
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
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'

    return response


# app.register_error_handler(404, page_not_found)
def page_not_found(_):
    return http_response(errorMsg='Resource not found'), 404


# app.register_error_handler(Exception, exception_handler)
def exception_handler(ex):
    return http_response(errorMsg='服务器开小差')
