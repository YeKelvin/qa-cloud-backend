#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_controller.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.system.controller import blueprint
from app.system.service import log_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/action/log/list')
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
    return service.query_action_log_list(req)
