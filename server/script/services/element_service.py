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
def query_element_list(req: RequestDTO):
    pass


@http_service
def query_element_all(req: RequestDTO):
    pass


@http_service
def create_element(req: RequestDTO):
    pass


@http_service
def modify_element(req: RequestDTO):
    pass


@http_service
def delete_element(req: RequestDTO):
    pass


def generate_element_no():
    seq_item_no = Sequence('seq_element_no')
    return 'EL' + str(seq_item_no.next_value()).zfill(10)
