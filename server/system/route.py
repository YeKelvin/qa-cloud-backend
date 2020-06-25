#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from flask import Blueprint

from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.system import service
from server.utils.log_util import get_logger

log = get_logger(__name__)

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
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_action_log_list(req)
