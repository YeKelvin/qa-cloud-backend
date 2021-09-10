#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : report_service.py
# @Time    : 2021-09-09 21:15:02
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_test_report_list(req):
    pass


@http_service
def query_test_report_all(req):
    pass


@http_service
def query_test_report_info(req):
    pass
