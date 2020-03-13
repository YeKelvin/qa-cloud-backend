#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_header_service
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def http_header_list(req: RequestDTO):
    """分页查询 HTTP头部列表
    """
    pass


@http_service
def http_header_all(req: RequestDTO):
    """查询所有 HTTP头部
    """
    pass


@http_service
def create_http_header(req: RequestDTO):
    """新增 HTTP头部
    """
    pass


@http_service
def modify_http_header(req: RequestDTO):
    """修改 HTTP头部
    """
    pass


@http_service
def delete_http_header(req: RequestDTO):
    """删除 HTTP头部
    """
    pass
