#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : exceptions.py
# @Time    : 2019/11/7 11:55
# @Author  : Kelvin.Ye
from enum import Enum, unique


class ServiceError(Exception):
    """业务异常类
    """

    def __init__(self, msg=None, code=None, error: 'ErrorCode' = None):
        super().__init__(self)
        if error is None:
            self.message = msg
            self.code = code
        else:
            self.message = error.value
            self.code = code.name


class ParseError(Exception):
    """请求参数解析异常类
    """

    def __init__(self, msg=None):
        self.message = msg


@unique
class ErrorCode(Enum):
    """
    业务错误码枚举

    错误码命名规范：E前缀+后三位数，后三位数从000开始递增
    +-----------------------+
    |错误码      |描述
    +-----------------------+
    |200        |成功
    |201        |已存在
    |401        |未授权
    |403        |禁止
    |404        |不存在
    |405        |状态异常
    |415        |格式错误
    |500        |内部错误
    +-----------------------+
    """
    # 200
    E200000 = '成功'

    # 201
    E201000 = '已存在'

    # 401
    E401000 = '未授权'
    E401001 = '用户未登录'
    E401002 = '用户无权限'

    # 403
    E403000 = '禁止操作'

    # 404
    E404000 = '不存在'

    # 405
    E405000 = '状态异常'

    # 415
    E415000 = '格式错误'

    # 500
    E500000 = '内部错误'
