#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_controller.py
# @Time    : 2020/3/17 14:31
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.enum import TestPhase
from app.script.enum import TestplanState
from app.script.service import testplan_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/testplan/list')
@require_login
@require_permission
def query_testplan_list():
    """分页查询测试计划列表"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间不能为空'),
        Argument('planNo'),
        Argument('planName'),
        Argument('versionNumber'),
        Argument('environment'),
        Argument('testPhase', enum=TestPhase),
        Argument('state', enum=TestplanState),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_testplan_list(req)


@blueprint.get('/testplan')
@require_login
@require_permission
def query_testplan():
    """查询测试计划详情"""
    req = JsonParser(Argument('planNo', required=True, nullable=False, help='计划编号不能为空')).parse()
    return service.query_testplan(req)


@blueprint.post('/testplan')
@require_login
@require_permission
def create_testplan():
    """创建测试计划"""
    req = JsonParser(
        Argument('planName', required=True, nullable=False, help='计划名称不能为空'),
        Argument('planDesc'),
        Argument('versionNumber'),
        Argument('environment'),
        Argument('collectionList', type=list, required=True, nullable=False, help='集合列表不能为空'),
        Argument('datasetNumberList', type=list),
        Argument('concurrency', default=1),
        Argument('iterations', default=1),
        Argument('delay', default=0),
        Argument('save', default=True),
        Argument('saveOnError', default=False),
        Argument('stopTestOnErrorCount', default=3),
        Argument('useCurrentValue', default=False),
        Argument('executeNow', default=True)
    ).parse()
    return service.execute_testplan(req)


@blueprint.put('/testplan')
@require_login
@require_permission
def modify_testplan():
    """修改测试计划"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('planName', required=True, nullable=False, help='计划名称不能为空'),
        Argument('planDesc'),
        Argument('versionNumber'),
        Argument('environment'),
        Argument('collectionList', type=list, required=True, nullable=False, help='集合列表不能为空'),
        Argument('datasetNumberList', type=list),
        Argument('concurrency', default=1),
        Argument('iterations', default=1),
        Argument('delay', default=0),
        Argument('save', default=True),
        Argument('saveOnError', default=False),
        Argument('stopTestOnErrorCount', default=3),
        Argument('useCurrentValue', default=False)
    ).parse()
    return service.modify_testplan(req)


@blueprint.patch('/testplan/state')
@require_login
@require_permission
def modify_testplan_state():
    """修改测试计划状态"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('state', required=True, nullable=False, enum=TestplanState, help='状态不能为空')
    ).parse()
    return service.modify_testplan_state(req)


@blueprint.patch('/testplan/testphase')
@require_login
@require_permission
def modify_testplan_testphase():
    """修改测试计划测试阶段"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('testPhase', required=True, nullable=False, enum=TestPhase, help='测试阶段不能为空')
    ).parse()
    return service.modify_testplan_testphase(req)


@blueprint.get('/testplan/execution/all')
@require_login
@require_permission
def query_testplan_execution_all():
    """查询所有测试计划执行记录"""
    req = JsonParser(Argument('planNo', required=True, nullable=False, help='计划编号不能为空')).parse()
    return service.query_testplan_execution_all(req)


@blueprint.get('/testplan/execution/details')
@require_login
@require_permission
def query_testplan_execution_details():
    """查询测试计划执行记录详情"""
    req = JsonParser(Argument('executionNo', required=True, nullable=False, help='执行编号不能为空')).parse()
    return service.query_testplan_execution_details(req)


@blueprint.get('/testplan/report')
@require_login
@require_permission
def query_testplan_report():
    """查询测试报告"""
    req = JsonParser(Argument('planNo', required=True, nullable=False, help='报告编号不能为空')).parse()
    return service.query_testplan_report(req)
