#!/usr/bin python3
# @File    : data_controller.py
# @Time    : 2023-09-25 14:29:32
# @Author  : Kelvin.Ye
from app.modules.system.controller import blueprint
from app.modules.system.service import data_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/data/log')
@require_login
@require_permission('QUERY_LOG')
def query_data_log():
    """查询数据日志"""
    req = JsonParser(
        Argument('logNo', required=True, nullable=False, help='日志编号不能为空')
    ).parse()
    return service.query_data_log(req)


@blueprint.get('/data/trace')
@require_login
@require_permission('QUERY_LOG')
def query_data_trace():
    """查询数据变更详情"""
    req = JsonParser(
        Argument('rowid')
    ).parse()
    return service.query_data_trace(req)


@blueprint.get('/data/log/list')
@require_login
@require_permission('QUERY_LOG')
def query_data_log_list():
    """分页查询数据日志列表"""
    req = JsonParser(
        Argument('startTime'),
        Argument('endTime'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_data_log_list(req)
