#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def element_list(req: RequestDTO):
    """分页查询测试元素列表
    """
    pass


@http_service
def element_all(req: RequestDTO):
    """查询所有测试元素
    """
    pass


@http_service
def create_element(req: RequestDTO):
    """新增测试元素
    """
    pass


@http_service
def modify_element(req: RequestDTO):
    """修改测试元素
    """
    pass


@http_service
def delete_element(req: RequestDTO):
    """删除测试元素
    """
    pass


def generate_element_no():
    seq_item_no = Sequence('seq_element_no')
    return 'EL' + str(seq_item_no.next_value()).zfill(10)
