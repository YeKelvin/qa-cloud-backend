#!/usr/bin python3
# @File    : apilog_controller.py
# @Time    : 2023-04-21 09:01:42
# @Author  : Kelvin.Ye
from app.modules.opencenter.controller import blueprint
from app.modules.opencenter.service import apilog_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/openapi/log/list')
@require_login
@require_permission('QUERY_OPENAPI_LOG')
def query_openapi_log_list():
    """分页查询OpenAPI日志列表"""
    req = JsonParser(
        Argument('appName'),
        Argument('method'),
        Argument('path'),
        Argument('request'),
        Argument('response'),
        Argument('success'),
        Argument('startTime'),
        Argument('endTime'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_openapi_log_list(req)
