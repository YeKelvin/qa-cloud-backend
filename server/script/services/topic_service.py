#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : topic_service
# @Time    : 2020/3/13 16:56
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def topic_list(req: RequestDTO):
    """分页查询测试主题列表
    """
    pass


@http_service
def topic_all(req: RequestDTO):
    """查询所有测试主题
    """
    pass


@http_service
def create_topic(req: RequestDTO):
    """新增测试主题
    """
    pass


@http_service
def modify_topic(req: RequestDTO):
    """修改测试主题
    """
    pass


@http_service
def delete_topic(req: RequestDTO):
    """删除测试主题
    """
    pass
