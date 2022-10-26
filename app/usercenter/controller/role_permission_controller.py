#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_controller.py
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.usercenter.controller import blueprint
from app.usercenter.service import role_permission_service as service


log = get_logger(__name__)


@blueprint.get('/role/permissions')
@require_login
@require_permission
def query_role_permissions():
    """查询角色全部权限"""
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空')
    ).parse()
    return service.query_role_permissions(req)


@blueprint.post('/role/permissions')
@require_login
@require_permission
def set_role_permissions():
    """设置角色权限"""
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空'),
        Argument('permissionNumbers', type=list)
    ).parse()
    return service.set_role_permissions(req)
