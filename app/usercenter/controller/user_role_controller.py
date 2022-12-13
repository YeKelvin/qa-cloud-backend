#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_controller.py
# @Time    : 2020/7/3 15:13
# @Author  : Kelvin.Ye
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.usercenter.controller import blueprint
from app.usercenter.service import user_role_service as service


log = get_logger(__name__)


@blueprint.get('/user/role/list')
@require_login
@require_permission('QUERY_USER')
def query_user_role_list():
    """分页查询用户角色列表"""
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
        Argument('userName'),
        Argument('roleName'),
        Argument('roleCode'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_user_role_list(req)


@blueprint.get('/user/role/all')
@require_login
@require_permission('QUERY_USER')
def query_user_role_all():
    """查询全部用户角色"""
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
        Argument('userName'),
        Argument('roleName'),
        Argument('roleCode')
    ).parse()
    return service.query_user_role_all(req)
