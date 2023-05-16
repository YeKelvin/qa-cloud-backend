#!/usr/bin python3
# @File    : running_controller.py
# @Time    : 2023-04-20 14:34:42
# @Author  : Kelvin.Ye
from app.openapi.testing.controller import blueprint
from app.openapi.testing.service import testplan_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_thirdparty_access


@blueprint.post('/testplan/execution/details')
@require_thirdparty_access
def query_execution_details():
    """查询测试计划执行详情"""
    req = JsonParser(
        Argument('testplanNo', required=True, nullable=False, help='计划编号不能为空')
    ).parse()
    return service.query_execution_details(req)
