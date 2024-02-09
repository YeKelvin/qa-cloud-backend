#!/usr/bin/ python3
# @File    : execution_controller.py
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from app.modules.script.controller import blueprint
from app.modules.script.service import execution_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.post('/element/collection/run')
@require_login
@require_permission('RUN_ELEMENT')
def run_collection():
    """运行测试集合"""
    req = JsonParser(
        Argument('collectionNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('offlines', type=dict, default={}),
        Argument('socketId', required=True, nullable=False, help='SID不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('variables', type=dict, default={}),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.run_collection(req)


@blueprint.post('/element/worker/run')
@require_login
@require_permission('RUN_ELEMENT')
def run_worker():
    """运行测试用例"""
    req = JsonParser(
        Argument('workerNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('offlines', type=dict, default={}),
        Argument('socketId', required=True, nullable=False, help='SID不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('variables', type=dict, default={}),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.run_worker(req)


@blueprint.post('/element/worker/run-by-sampler')
@require_login
@require_permission('RUN_ELEMENT')
def run_worker_by_sampler():
    """根据请求编号运行测试用例"""
    req = JsonParser(
        Argument('samplerNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('offlines', type=dict, default={}),
        Argument('socketId', required=True, nullable=False, help='SID不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('variables', type=dict, default={}),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.run_worker_by_sampler(req)


@blueprint.post('/element/sampler/run')
@require_login
@require_permission('RUN_ELEMENT')
def run_sampler():
    """运行取样器"""
    req = JsonParser(
        Argument('samplerNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('aloneness', default=True),
        Argument('offlines', type=dict, default={}),
        Argument('socketId', required=True, nullable=False, help='SID不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('variables', type=dict, default={}),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.run_sampler(req)


@blueprint.post('/element/snippet/run')
@require_login
@require_permission('RUN_ELEMENT')
def run_snippet():
    """运行片段集合"""
    req = JsonParser(
        Argument('snippetNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('offlines', type=dict, default={}),
        Argument('socketId', required=True, nullable=False, help='SID不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('variables', type=dict, default={}),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.run_snippet(req)


@blueprint.post('/element/offline/run')
@require_login
@require_permission('RUN_ELEMENT')
def run_offline():
    """运行离线请求"""
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('aloneness', default=False),
        Argument('offlineNo', required=True, nullable=False, help='离线编号不能为空'),
        Argument('offlines', type=dict, required=True, nullable=False, help='离线数据不能为空'),
        Argument('socketId', required=True, nullable=False, help='SID不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('variables', type=dict, default={}),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.run_offline(req)


@blueprint.post('/testplan/execute')
@require_login
@require_permission('RUN_TESTPLAN')
def execute_testplan():
    """运行测试计划"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.execute_testplan(req)


@blueprint.post('/testplan/interrupt')
@require_login
@require_permission('INTERRUPT_TESTPLAN')
def interrupt_testplan():
    """中断运行测试计划"""
    req = JsonParser(
        Argument('executionNo', required=True, nullable=False, help='执行编号不能为空')
    ).parse()
    return service.interrupt_testplan(req)
