#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
import traceback

from sendanywhere.runner import Runner

from app.common.decorators.service import http_service
from app.common.request import RequestDTO
from app.extension import executor
from app.script.services import execution_helper as helper
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def execute_script(req: RequestDTO):
    # 根据collectionNo递归查询脚本数据并转换成dict
    collection = helper.element_to_dict(req.attr.collectionNo)

    # TODO: 增加脚本完整性校验，例如脚本下是否有内容

    if req.attr.sid:
        add_flask_socketio_result_collector_component(collection, req.attr.sid)

    script = [collection]
    # 新增线程执行脚本
    # TODO: 暂时用ThreadPoolExecutor，后面改用Celery，https://www.celerycn.io/

    def start():
        try:
            Runner.start(script)
        except Exception:
            log.error(traceback.format_exc())

    executor.submit(start)
    return None


def add_flask_socketio_result_collector_component(script: dict, sid: str):
    script['child'].insert(0, {
        'name': 'FlaskSocketIOResultCollector',
        'comments': None,
        'class': 'FlaskSocketIOResultCollector',
        'enabled': True,
        'property': {
            'FlaskSocketIOResultCollector__namespace': '/',
            'FlaskSocketIOResultCollector__event_name': 'execution_result',
            'FlaskSocketIOResultCollector__target_sid': sid,
            'FlaskSocketIOResultCollector__flask_sio_instance_module': 'server.extension',
            'FlaskSocketIOResultCollector__flask_sio_instance_name': 'socketio',
        },
        'child': None
    })
