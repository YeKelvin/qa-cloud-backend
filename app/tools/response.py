#!/usr/bin/ python3
# @File    : response.py
# @Time    : 2019/11/7 11:52
# @Author  : Kelvin.Ye
from datetime import datetime
from datetime import timezone
from enum import Enum

from flask import make_response

from app.tools.enums import HttpStatus
from app.tools.exceptions import ErrorCode
from app.utils.json_util import to_json


class ResponseDTO:
    """请求响应对象"""

    def __init__(
        self,
        result: any = None,
        success: bool = True,
        error: ErrorCode = None,
        errorCode: str = None,  # noqa
        errorMsg: str = None  # noqa
    ):
        self.result = result
        self.success = success
        if error is None:
            self.errorCode = errorCode
            self.errorMsg = errorMsg
        else:
            self.errorCode = error.name
            self.errorMsg = error.value
        # 可覆盖枚举的msg
        if error and errorMsg:
            self.errorMsg = errorMsg
        if error or errorCode or errorMsg:
            self.success = False
        self.timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


def http_response(res: ResponseDTO = None, status: Enum = HttpStatus.CODE_200, **kwargs):
    if not res:
        res = ResponseDTO(**kwargs)

    response = make_response(to_json(res.__dict__), status.value)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response
