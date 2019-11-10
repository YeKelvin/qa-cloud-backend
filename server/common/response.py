#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : dto.py
# @Time    : 2019/11/7 11:52
# @Author  : Kelvin.Ye
from enum import Enum

from flask import make_response

from server.common.exception import ErrorCode
from server.common.status import Status
from server.utils.json_util import to_json


class BaseResponse:
    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class Response(BaseResponse):
    def __init__(self,
                 result: any = None,
                 success: bool = True,
                 error: ErrorCode = None,
                 errorCode: str = None,
                 errorMsg: str = None):
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

    def set_result(self, result: any) -> None:
        self.result = result
        self.success = True

    def set_error(self, error_code: Enum) -> None:
        self.errorCode = error_code.name
        self.errorMsg = error_code.value
        self.success = False


def http_response(result: any = None,
                  error: ErrorCode = None,
                  status: Enum = Status.CODE_200):
    res = Response(result, error=error)
    res_json = to_json(res.__dict__)
    response = make_response(res_json, status.value)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response
