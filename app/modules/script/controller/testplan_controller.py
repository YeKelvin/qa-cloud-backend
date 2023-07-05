#!/usr/bin/ python3
# @File    : testplan_controller.py
# @Time    : 2020/3/17 14:31
# @Author  : Kelvin.Ye
from app.modules.script.controller import blueprint
from app.modules.script.enum import TestPhase
from app.modules.script.enum import TestplanState
from app.modules.script.service import testplan_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/testplan/list')
@require_login
@require_permission('QUERY_TESTPLAN')
def query_testplan_list():
    """分页查询测试计划列表"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间不能为空'),
        Argument('planNo'),
        Argument('planName'),
        Argument('scrumVersion'),
        Argument('scrumSprint'),
        Argument('testPhase'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_testplan_list(req)


@blueprint.get('/testplan/all')
@require_login
@require_permission('QUERY_TESTPLAN')
def query_testplan_all():
    """查询全部测试计划"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间不能为空'),
        Argument('stateList', type=list),
    ).parse()
    return service.query_testplan_all(req)


@blueprint.get('/testplan')
@require_login
@require_permission('QUERY_TESTPLAN')
def query_testplan():
    """查询测试计划详情"""
    req = JsonParser(Argument('planNo', required=True, nullable=False, help='计划编号不能为空')).parse()
    return service.query_testplan(req)


@blueprint.post('/testplan')
@require_login
@require_permission('CREATE_TESTPLAN')
def create_testplan():
    """新增测试计划"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('planName', required=True, nullable=False, help='计划名称不能为空'),
        Argument('planDesc'),
        Argument('scrumVersion'),
        Argument('scrumSprint'),
        Argument('collectionList', type=list, required=True, nullable=False, help='集合列表不能为空'),
        Argument('concurrency', default=1),
        Argument('iterations', default=1),
        Argument('delay', default=0),
        Argument('save', default=True),
        Argument('saveOnError', default=False),
        Argument('stopOnErrorCount', default=3),
        Argument('notificationRobots', type=list),
    ).parse()
    return service.create_testplan(req)


@blueprint.put('/testplan')
@require_login
@require_permission('MODIFY_TESTPLAN')
def modify_testplan():
    """修改测试计划"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('planName', required=True, nullable=False, help='计划名称不能为空'),
        Argument('planDesc'),
        Argument('scrumVersion'),
        Argument('scrumSprint'),
        Argument('collectionList', type=list, required=True, nullable=False, help='集合列表不能为空'),
        Argument('concurrency', default=1),
        Argument('iterations', default=1),
        Argument('delay', default=0),
        Argument('save', default=True),
        Argument('saveOnError', default=False),
        Argument('stopOnErrorCount', default=3)
    ).parse()
    return service.modify_testplan(req)


@blueprint.put('/testplan/state')
@require_login
@require_permission('MODIFY_TESTPLAN')
def modify_testplan_state():
    """修改测试计划状态"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('state', required=True, nullable=False, enum=TestplanState, help='状态不能为空')
    ).parse()
    return service.modify_testplan_state(req)


@blueprint.put('/testplan/testphase')
@require_login
@require_permission('MODIFY_TESTPLAN')
def modify_testplan_testphase():
    """修改测试计划测试阶段"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('testPhase', required=True, nullable=False, enum=TestPhase, help='测试阶段不能为空')
    ).parse()
    return service.modify_testplan_testphase(req)


@blueprint.get('/testplan/execution/all')
@require_login
@require_permission('QUERY_TESTPLAN_EXECUTION')
def query_testplan_execution_all():
    """查询全部执行记录"""
    req = JsonParser(Argument('planNo', required=True, nullable=False, help='计划编号不能为空')).parse()
    return service.query_testplan_execution_all(req)


@blueprint.get('/testplan/execution/details')
@require_login
@require_permission('QUERY_TESTPLAN_EXECUTION')
def query_testplan_execution_details():
    """查询执行记录详情"""
    req = JsonParser(Argument('executionNo', required=True, nullable=False, help='执行编号不能为空')).parse()
    return service.query_testplan_execution_details(req)
