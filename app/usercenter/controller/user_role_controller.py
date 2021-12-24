#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_controller.py
# @Time    : 2020/7/3 15:13
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.usercenter.controller import blueprint
from app.usercenter.service import user_role_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/user/role/list')
@require_login
@require_permission
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
@require_permission
def query_user_role_all():
    """查询所有用户角色"""
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
        Argument('userName'),
        Argument('roleName'),
        Argument('roleCode')
    ).parse()
    return service.query_user_role_all(req)
