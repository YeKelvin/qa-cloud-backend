#!/usr/bin python3
# @File    : running_controller.py
# @Time    : 2023-04-20 14:34:42
# @Author  : Kelvin.Ye
from app.openapi.scriptcenter.controller import blueprint
from app.openapi.scriptcenter.service import running_service as service
from app.tools.decorators.require import require_thirdparty_access
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.post('/testplan/execute')
@require_thirdparty_access
def execute_testplan():
    """执行测试计划"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.execute_testplan(req)
