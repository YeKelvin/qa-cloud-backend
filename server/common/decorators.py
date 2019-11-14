#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : decorators.py
# @Time    : 2019/11/7 15:41
# @Author  : Kelvin.Ye
import traceback
from functools import wraps

from flask import request

from main import app
from server.common.exception import ServiceError, ErrorCode
from server.common.response import http_response, ResponseDTO
from server.utils.log_util import get_logger
from server.utils.time_util import current_time_as_ms

log = get_logger(__name__)


def http_service(func):
    """service层函数装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 记录开始时间
        starttime = current_time_as_ms()
        log.info(
            rf'logId:[ logId ] method:[{request.method}] path:[{request.path}] request:[ request ]')
        res = None
        try:
            # 函数调用
            res = func(*args, **kwargs)
        except ServiceError as err:
            res = ResponseDTO()
            res.errorCode = err.code
            res.errorMsg = err.message
            res.success = False
        except Exception:
            traceback.print_exc()
            res = ResponseDTO()
            res.errorCode = ErrorCode.ERROR_CODE_500000.name
            res.errorMsg = ErrorCode.ERROR_CODE_500000.value
            res.success = False
        finally:
            # 计算耗时ms
            elapsed_time = current_time_as_ms() - starttime
            log.info(
                rf'logId:[ logId ] method:[{request.method}] path:[{request.path}] '
                rf'response:[ {res} ] elapsed:[{elapsed_time}ms]')
            return http_response(res)

    return wrapper


def require_login():
    pass


def require_permission():
    pass


def with_app_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)

    return wrapper
