#!/usr/bin/ python3
# @File    : hook.py
# @Time    : 2019/11/7 20:02
# @Author  : Kelvin.Ye
from flask import g
from flask import request

from app.tools.identity import new_ulid
from app.tools.response import http_response


def inject_traceid():
    """注入traceid"""
    trace_id = getattr(g, 'trace_id', None)
    if not trace_id:
        g.trace_id = new_ulid()


def inject_ip():
    """注入请求ip"""
    if x_forwarded_for := request.headers.get('X-Forwarded-For'):
        ip_list = x_forwarded_for.split(',')
        g.ip = ip_list[0]
    else:
        g.ip = request.remote_addr


def cross_domain_access(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'

    if request.method == 'OPTIONS':
        response.headers['Access-Control-Max-Age'] = 60 * 60 * 24
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'

    return response


# app.register_error_handler(404, page_not_found)
def page_not_found(_):
    return http_response(msg='Resource not found', code=500), 404


# app.register_error_handler(Exception, exception_handler)
def exception_handler(ex):
    return http_response(msg='服务器开小差', code=500)
