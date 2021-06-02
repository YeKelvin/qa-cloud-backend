#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_header_service.py
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.request import RequestDTO
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_http_header_list(req: RequestDTO):
    pass


@http_service
def query_http_header_all(req: RequestDTO):
    pass


@http_service
def create_http_header(req: RequestDTO):
    pass


@http_service
def modify_http_header(req: RequestDTO):
    pass


@http_service
def delete_http_header(req: RequestDTO):
    pass
