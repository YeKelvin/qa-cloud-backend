#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : dto.py
# @Time    : 2019/11/7 11:52
# @Author  : Kelvin.Ye
from enum import Enum

from flask import make_response

from server.common.exception import ErrorCode
from server.common.helpers.global_helper import Global
from server.common.status import Status
from server.common.utils.json_util import to_json


class ResponseDTO:
    """请求响应对象
    """

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

    def set_error(self, error: Enum) -> None:
        self.errorCode = error.name
        self.errorMsg = error.value
        self.success = False

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


def http_response(res: ResponseDTO = None,
                  status: Enum = Status.CODE_200,
                  **kwargs):
    if not res:
        res = ResponseDTO(**kwargs)
    res_json = to_json(res.__dict__)
    response = make_response(res_json, status.value)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    Global.set('success', res.success)
    return response
