#!/usr/bin/ python3
# @File    : log_controller.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.modules.system.controller import blueprint
from app.modules.system.service import apilog_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/restapi/log/list')
@require_login
@require_permission('QUERY_LOG')
def query_restapi_log_list():
    """分页查询操作日志列表"""
    req = JsonParser(
        Argument('method'),
        Argument('path'),
        Argument('request'),
        Argument('response'),
        Argument('success'),
        Argument('startTime'),
        Argument('endTime'),
        Argument('invokeBy'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_restapi_log_list(req)
