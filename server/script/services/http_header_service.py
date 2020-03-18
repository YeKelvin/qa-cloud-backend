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


def generate_header_no():
    seq_topic_no = Sequence('seq_http_header_no')
    return 'H' + str(seq_topic_no.next_value()).zfill(10)
