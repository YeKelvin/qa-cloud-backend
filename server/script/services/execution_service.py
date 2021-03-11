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

    # TODO: 增加脚本完整性校验，例如脚本下是否有内容

    if req.attr.sid:
        add_socket_result_collector_component(script, req.attr.sid)

    # 新增线程执行脚本
    # TODO: 暂时用ThreadPoolExecutor，后面改用Celery，https://www.celerycn.io/
    executor.submit(Runner.start, script)

    return None


def add_socket_result_collector_component(script: dict, sid: str):
    component = {
        'name': 'SocketResultCollector',
        'comments': None,
        'class': 'SocketResultCollector',
        'enabled': True,
        'property': {
            'SocketResultCollector__url': '',
            'SocketResultCollector__headers': None,
            'SocketResultCollector__namespace': None,
            'SocketResultCollector__event_name': 'execution_result',
            'SocketResultCollector__target_sid': sid
        },
        'child': None
    }
    collection_children = script['child']
    collection_children.insert(0, component)
