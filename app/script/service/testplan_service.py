#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_service.py
# @Time    : 2020/3/17 14:32
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_xxx_list(req):
    pass


@http_service
def query_xxx_all(req):
    pass
