#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
import traceback
from functools import wraps

from flask import request, g

from server.librarys.exception import ServiceError, ErrorCode
from server.librarys.request import RequestDTO
from server.librarys.response import http_response, ResponseDTO
from server.utils.log_util import get_logger
from server.utils.time_util import timestamp_as_ms

log = get_logger(__name__)


def http_service(func):
    """service层装饰器，主要用于记录日志和捕获异常
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        req: RequestDTO = (args[0] if args else None) or kwargs.get('req', RequestDTO())
        # 记录开始时间
        starttime = timestamp_as_ms()
        log.info(
            f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
            f'header:[ {dict(request.headers)} ] request:[ {req.attr} ]'
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
            elapsed_time = timestamp_as_ms() - starttime
            http_res = http_response(res)
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'header:[ {dict(http_res.headers)}] response:[ {res} ] '
                f'elapsed:[ {elapsed_time}ms ]'
            )
            return http_res

    return wrapper
