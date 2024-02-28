#!/usr/bin/ python3
# @File    : response.py
# @Time    : 2019/11/7 11:52
# @Author  : Kelvin.Ye
from datetime import UTC
from datetime import datetime
from enum import Enum

from flask import make_response

from app.tools.enums import HTTPStatus
from app.tools.exceptions import ServiceStatus
from app.utils.json_util import to_json


class ResponseDTO:
    """请求响应对象"""

    def __init__(
        self,
        data: any = None,
        *,
        msg: str = None,
        code: str = ServiceStatus.CODE_200.CODE
    ):
        self.data = data
        self.code = code
        self.message = msg
        if msg and not code:
            self.code = ServiceStatus.CODE_600.CODE
        self.timestamp = datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


def http_response(res: ResponseDTO = None, status: Enum = HTTPStatus.CODE_200, **kwargs):
    if not res:
        res = ResponseDTO(**kwargs)

    response = make_response(to_json(res.__dict__), status.value)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response
