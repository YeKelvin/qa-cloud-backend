#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from sendanywhere.runner import Runner
from server.common.decorators.service import http_service
from server.common.request import RequestDTO
from server.common.utils.log_util import get_logger
from server.extension import executor
from server.script.services import execution_helper as helper

log = get_logger(__name__)


@http_service
def execute_script(req: RequestDTO):
    # 根据collectionNo递归查询脚本数据并转换成dict
    script = [helper.element_to_dict(req.attr.collectionNo)]

    # 新增线程执行脚本
    # TODO: 暂时用ThreadPoolExecutor，后面改用Celery
    # https://www.celerycn.io/
    executor.submit(Runner.start, script)

    return None
