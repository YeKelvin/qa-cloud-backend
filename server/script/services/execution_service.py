#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from server.common.decorators.service import http_service
from server.common.request import RequestDTO
from server.common.utils.log_util import get_logger
from server.script.services import execution_helper as helper
from sendanywhere.runner import Runner

log = get_logger(__name__)


@http_service
def execute_script(req: RequestDTO):
    # 根据collectionNo递归查询脚本数据并转换成dict
    script = [helper.element_to_dict(req.attr.collectionNo)]

    # 开始执行脚本
    Runner.start(script)
