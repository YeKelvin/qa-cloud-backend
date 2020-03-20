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
def query_element_package_list(req: RequestDTO):
    pass


@http_service
def query_element_package_all(req: RequestDTO):
    pass


__seq_package_no__ = Sequence('seq_package_no')


def generate_package_no():
    return 'EP' + str(__seq_package_no__.next_value()).zfill(10)
