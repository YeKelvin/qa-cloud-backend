#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_service.py
# @Time    : 2021/1/27 09:19
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.request import RequestDTO
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def test_run(req: RequestDTO):
    return ''
