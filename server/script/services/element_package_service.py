#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_package_service
# @Time    : 2020/3/17 14:32
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def element_package_list(req: RequestDTO):
    """分页查询元素封装列表
    """
    pass


@http_service
def element_package_all(req: RequestDTO):
    """查询所有元素封装
    """
    pass


def generate_package_no():
    seq_item_no = Sequence('seq_package_no')
    return 'EP' + str(seq_item_no.next_value()).zfill(10)
