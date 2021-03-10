#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from flask import Blueprint

from server.common.decorators.require import require_login, require_permission
from server.common.parser import JsonParser, Argument
from server.system import services
from server.common.utils.log_util import get_logger

log = get_logger(__name__)

# TODO: prefix修改为 /rest/api/{v+版本号}/{module}/{resource}
# TODO: 响应报文的Header添加名为 API-Version 的头，值为 day-month-year 格式的日期
blueprint = Blueprint('system', __name__, url_prefix='/system')


@blueprint.route('/action/log/list', methods=['GET'])
@require_login
@require_permission
def query_action_log_list():
    """分页查询操作日志列表
    """
    req = JsonParser(
        Argument('actionDesc'),
        Argument('actionMethod'),
        Argument('actionEndpoint'),
        Argument('createdBy'),
        Argument('startTime'),
        Argument('endTime'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return services.query_action_log_list(req)
