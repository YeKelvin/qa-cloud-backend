#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_controller.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.usercenter.controller import blueprint
from app.usercenter.service import permission_service as service


log = get_logger(__name__)


@blueprint.get('/permission/all')
@require_login
@require_permission('QUERY_PERMISSION')
def query_permission_all():
    """查询全部权限"""
    req = JsonParser(
        Argument('moduleCodes', type=list),
        Argument('objectCodes', type=list),
        Argument('actExcludes', type=list),
    ).parse()
    return service.query_permission_all(req)
