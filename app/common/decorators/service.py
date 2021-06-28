#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
import inspect
import traceback
from functools import wraps

from flask import g
from flask import request

from app.common.exceptions import ErrorCode
from app.common.exceptions import ServiceError
from app.common.request import RequestDTO
from app.common.response import ResponseDTO
from app.common.response import http_response
from app.utils.time_util import timestamp_as_ms


def http_service(func):
    """service层装饰器，主要用于记录日志和捕获异常"""
    log = inspect.getmodule(func).log

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取请求对象
        req: RequestDTO = (args[0] if args else None) or kwargs.get('req', RequestDTO())
        # 记录开始时间
        starttime = timestamp_as_ms()
        error = req.pop('error', None)
        log.info(
            f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
            f'header:[ {dict(request.headers)} ] request:[ {req} ]'
        )
        res = None
        try:
            # 判断request参数解析是否有异常
            if error is not None:
                res = ResponseDTO(errorMsg=error)
            else:
                # 调用service
                result = func(*args, **kwargs)
                res = ResponseDTO(result)
                log.info(
                    f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] result:[ {result} ]'
                )
        except ServiceError as err:
            # 捕获service层的业务异常
            res = ResponseDTO(errorMsg=err.message, errorCode=err.code)
        except Exception:
            # 捕获所有异常
            log.error(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'traceback:\n{traceback.format_exc()}'
            )
            res = ResponseDTO(error=ErrorCode.E500000)
        finally:
            # 记录接口耗时（毫秒）
            elapsed_time = timestamp_as_ms() - starttime
            # 包装http响应
            http_res = http_response(res)
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'header:[ {dict(http_res.headers)}] response:[ {res} ] '
                f'elapsed:[ {elapsed_time}ms ]'
            )
            return http_res

    return wrapper
