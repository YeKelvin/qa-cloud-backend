#!/usr/bin/ python3
# @File    : service.py
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
from functools import wraps

from flask import g
from flask import request
from loguru import logger

from app.tools.exceptions import ErrorCode
from app.tools.exceptions import ServiceError
from app.tools.request import RequestDTO
from app.tools.response import ResponseDTO
from app.tools.response import http_response
from app.utils.time_util import timestamp_as_ms


def http_service(func):
    """service层装饰器，主要用于记录日志和捕获异常"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 记录开始时间
        starttime = timestamp_as_ms()
        # 获取请求对象
        req: RequestDTO = (args[0] if args else None) or kwargs.get('req', RequestDTO())
        # 请求路径
        uri = f'{request.method} {request.path}'
        # 更新logger的record，使其指向被装饰的函数
        tlogger = logger.patch(lambda r: r.update(module=func.__module__, function=func.__name__))
        # 注入traceid
        with logger.contextualize(traceid=g.trace_id):
            # 输出http请求日志
            tlogger.info(f'uri:[ {uri} ] header:[ {dict(request.headers)} ] request:[ {req} ]')
            res = None
            try:
                # 判断request参数解析是否有异常
                if req.__error__ is not None:
                    res = ResponseDTO(errorMsg=req.__error__)
                else:
                    # 调用service
                    result = func(*args, **kwargs)
                    res = ResponseDTO(result)
            except ServiceError as err:
                # 捕获service层的业务异常
                res = ResponseDTO(errorMsg=err.message, errorCode=err.code)
            except Exception:
                tlogger.exception(f'uri:[ {uri} ]')
                res = ResponseDTO(error=ErrorCode.E500000)
            finally:
                # 记录接口耗时（毫秒）
                elapsed_time = timestamp_as_ms() - starttime
                # 包装http响应
                http_res = http_response(res)
                # 输出http响应日志
                tlogger.info(
                    f'uri:[ {uri} ] header:[ {dict(http_res.headers)}] response:[ {res} ] elapsed:[ {elapsed_time}ms ]'
                )
                return http_res

    return wrapper
