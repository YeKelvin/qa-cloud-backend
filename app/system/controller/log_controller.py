#!/usr/bin/ python3
# @File    : log_controller.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.system.controller import blueprint
from app.system.service import log_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.get('/operation/log/list')
@require_login
@require_permission('QUERY_LOG')
def query_operation_log_list():
    """分页查询操作日志列表"""
    req = JsonParser(
        Argument('operationMethod'),
        Argument('operationEndpoint'),
        Argument('operationName'),
        Argument('operationBy'),
        Argument('startTime'),
        Argument('endTime'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_operation_log_list(req)
