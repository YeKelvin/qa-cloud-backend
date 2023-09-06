#!/usr/bin python3
# @File    : login_log_controller.py
# @Time    : 2023-09-06 16:12:19
# @Author  : Kelvin.Ye
from app.modules.usercenter.controller import blueprint
from app.modules.usercenter.service import login_log_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/login/log/list')
@require_login
@require_permission('QUERY_LOG')
def query_login_log_list():
    """分页查询操作日志列表"""
    req = JsonParser(
        Argument('userName'),
        Argument('loginName'),
        Argument('loginType'),
        Argument('loginMethod'),
        Argument('loginIp'),
        Argument('startTime'),
        Argument('endTime'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_login_log_list(req)
