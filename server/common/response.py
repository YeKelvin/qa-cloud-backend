#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : dto.py
# @Time    : 2019/11/7 11:52
# @Author  : Kelvin.Ye
from enum import Enum

from flask import make_response

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
                 success: bool = False,
                 errorCode: str = None,
                 errorMsg: str = None) -> None:
        self.result = result
        self.success = success
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def set_result(self, result: any) -> None:
        self.result = result
        self.success = True

    def set_error(self, error_code: Enum) -> None:
        self.errorCode = error_code.name
        self.errorMsg = error_code.value
        self.success = False


def http_response(response_dto: Response(), status: Enum = Status.CODE_200):
    response_json = to_json(response_dto)
    response = make_response(response_json, status.value)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response
