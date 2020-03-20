#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO


@http_service
def execute_script(req: RequestDTO):
    pass
