#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_controller.py
# @Time    : 2020/3/17 14:31
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import testplan_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/testplan/list')
@require_login
@require_permission
def query_xxx_list():
    """分页查询元素封装列表
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_xxx_list(req)


@blueprint.get('/testplan/all')
@require_login
@require_permission
def query_xxx_all():
    """查询所有元素封装
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.query_xxx_all(req)
