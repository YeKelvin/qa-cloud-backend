#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from server.common.decorators.service import http_service
from server.common.request import RequestDTO


@http_service
def execute_script(req: RequestDTO):
    pass
