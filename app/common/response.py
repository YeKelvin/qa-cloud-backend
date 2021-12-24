#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : response.py
# @Time    : 2019/11/7 11:52
# @Author  : Kelvin.Ye
from datetime import datetime
from enum import Enum

from flask import make_response

from app.common import globals
from app.common.enums import HttpStatus
from app.common.exceptions import ErrorCode
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
        if error or errorCode or errorMsg:
            self.success = False
        self.responseTm = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


def http_response(res: ResponseDTO = None, status: Enum = HttpStatus.CODE_200, **kwargs):
    if not res:
        res = ResponseDTO(**kwargs)

    globals.put('success', res.success)
    res_json = to_json(res.__dict__)
    response = make_response(res_json, status.value)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response
