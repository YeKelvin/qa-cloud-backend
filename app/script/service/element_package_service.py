#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_package_service.py
# @Time    : 2020/3/17 14:32
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.request import RequestDTO
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_element_package_list(req: RequestDTO):
    pass


@http_service
def query_element_package_all(req: RequestDTO):
    pass
