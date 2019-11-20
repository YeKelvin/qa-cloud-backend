#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : decorators.py
# @Time    : 2019/11/7 15:41
# @Author  : Kelvin.Ye
import datetime
import traceback
from functools import wraps

from flask import request, g

from server.librarys.exception import ServiceError, ErrorCode
from server.librarys.request import RequestDTO
from server.librarys.response import http_response, ResponseDTO
from server.utils.log_util import get_logger
from server.utils.time_util import current_timestamp_as_ms

log = get_logger(__name__)


def http_service(func):
    """service层装饰器，主要用于记录日志和捕获异常
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        req: RequestDTO = args[0] or kwargs.get('req', RequestDTO())
        # 记录开始时间
        starttime = current_timestamp_as_ms()
        log.info(
            f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
            f'header:[ {dict(request.headers.to_list("utf-8"))} ] request:[ {req.attr} ]'
        )
        res = None
        try:
            # 判断 request参数解析是否有异常
            if req.error is None:
                # 函数调用
                result = func(*args, **kwargs)
                res = ResponseDTO(result)
                log.info(
                    f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                    f'result:[ {result} ]'
                )
            else:
                res = ResponseDTO(errorMsg=req.error)
        except ServiceError as err:
            # 捕获 service层的业务异常
            res = ResponseDTO(errorMsg=err.message, errorCode=err.code)
        except Exception:
            log.error(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'traceback:[ {traceback.format_exc()} ]'
            )
            res = ResponseDTO(error=ErrorCode.E500000)
        finally:
            # 计算耗时，单位毫秒
            elapsed_time = current_timestamp_as_ms() - starttime
            http_res = http_response(res)
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'header:[ {dict(http_res.headers.to_list("utf-8"))}] response:[ {res} ] '
                f'elapsed:[ {elapsed_time}ms ]'
            )
            return http_res

    return wrapper


def require_login(func):
    """登录校验装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_token = getattr(g, 'auth_token', None)
        auth_login_time = getattr(g, 'auth_login_time', None)
        user = getattr(g, 'user', None)
        # JWT解析 payload失败
        if not auth_token or not auth_login_time:
            log.debug('JWT解析 payload失败')
            return http_response(ResponseDTO(errorMsg='用户未登录'))

        # 查询 user失败或 user不存在
        if not user:
            log.debug('查询 user失败或 user不存在')
            return http_response(ResponseDTO(errorMsg='用户未登录'))

        # user已主动登出系统，需要重新登录
        if not user.access_token:
            log.debug('user已主动登出系统，需要重新登录')
            return http_response(ResponseDTO(errorMsg='用户未登录'))

        # user状态异常
        if user.state != 'NORMAL':
            log.debug(f'user状态异常 user.state:[ {user.state} ]')
            return http_response(ResponseDTO(errorMsg='用户状态异常，请联系管理员'))

        # user的 access_token已更变，不能使用旧 token认证
        if auth_token != user.access_token:
            log.debug('user的 access_token已更变，不能使用旧 token认证')
            return http_response(ResponseDTO(errorMsg='用户未登录'))

        # user 中的最后成功登录时间和 token中的登录时间不一致
        auth_login_time = datetime.datetime.fromtimestamp(auth_login_time)
        if auth_login_time != user.last_success_time:
            log.debug(f'user 中的最后成功登录时间和 token中的登录时间不一致 '
                      f'user.last_success_time:[ {user.last_success_time} ] '
                      f'auth_login_time:[ {auth_login_time} ]'
                      )
            return http_response(ResponseDTO(errorMsg='用户未登录'))

        return func(*args, **kwargs)

    return wrapper


@require_login
def require_permission(func):
    """权限校验装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
