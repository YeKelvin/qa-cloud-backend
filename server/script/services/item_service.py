#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def item_list(req: RequestDTO):
    """分页查询测试项目列表
    """
    pass


@http_service
def item_all(req: RequestDTO):
    """查询所有测试项目
    """
    pass


@http_service
def create_item(req: RequestDTO):
    """新增测试项目
    """
    pass


@http_service
def modify_item(req: RequestDTO):
    """修改测试项目
    """
    pass


@http_service
def delete_item(req: RequestDTO):
    """删除测试项目
    """
    pass

