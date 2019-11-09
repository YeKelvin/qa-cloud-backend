#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : exception.py
# @Time    : 2019/11/7 11:55
# @Author  : Kelvin.Ye
from enum import Enum, unique


class ServiceError(Exception):
    """业务异常类
    """

    def __init__(self, error_code: Enum, msg=None) -> None:
        super().__init__(self)
        self.code = error_code.name
        if msg is None:
            self.message = error_code.value
        else:
            self.message = msg

    def __str__(self):
        return f'{self.code} {self.message}'


@unique
class ErrorCode(Enum):
    """
    业务错误码枚举

    错误码命名规范：ERROR_CODE_前缀+后三位数，后三位数从000开始递增
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
    ERROR_CODE_200000 = '操作成功'

    # 201
    ERROR_CODE_201000 = '已存在'

    # 401
    ERROR_CODE_401000 = '用户未授权'

    # 403
    ERROR_CODE_403000 = '禁止操作'
    ERROR_CODE_403001 = '不允许为空'

    # 404
    ERROR_CODE_404000 = '不存在'
    ERROR_CODE_404001 = '该路径下不存在文件'
    ERROR_CODE_404002 = '路径不存在'
    ERROR_CODE_404003 = '文件不存在'

    # 405
    ERROR_CODE_405000 = '状态异常'

    # 415
    ERROR_CODE_415000 = '格式错误'

    # 500
    ERROR_CODE_500000 = '内部错误'
    ERROR_CODE_500001 = '系统忙，请稍后'
    ERROR_CODE_500002 = '序列已达最大值'
