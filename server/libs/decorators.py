#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : decorators.py
# @Time    : 2019/11/7 15:41
# @Author  : Kelvin.Ye
import traceback
from functools import wraps

from flask import request, g

from server.libs.exception import ServiceError, ErrorCode
from server.libs.request import RequestDTO
from server.libs.response import http_response, ResponseDTO
from server.utils.log_util import get_logger
from server.utils.time_util import current_timestamp_as_ms

log = get_logger(__name__)


def http_service(func):
    """service层装饰器，主要用户日志记录和捕获异常
    """

    @wraps(func)
    def wrapper(req: RequestDTO):
        # 记录开始时间
        starttime = current_timestamp_as_ms()
        log.info(
            f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] request:[ {req.attr} ]'
        )
        res = None
        try:
            if req.error is None:
                # 函数调用
                res = func(req)
            else:
                res = req.error
        except ServiceError as err:
            res = ResponseDTO(errorCode=err.code, errorMsg=err.message)
        except Exception:
            traceback.print_exc()
            res = ResponseDTO(error=ErrorCode.E500000)
        finally:
            # 计算耗时ms
            elapsed_time = current_timestamp_as_ms() - starttime
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'response:[ {res} ] elapsed:[ {elapsed_time}ms ]'
            )
            return http_response(res)

    return wrapper


def require_login():
    pass


def require_permission():
    pass
