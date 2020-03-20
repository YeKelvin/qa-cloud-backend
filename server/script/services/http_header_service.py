#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_header_service
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.utils.log_util import get_logger

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


__seq_http_header_no__ = Sequence('seq_http_header_no')


def generate_header_no():
    return 'HEADER' + str(__seq_http_header_no__.next_value()).zfill(10)
