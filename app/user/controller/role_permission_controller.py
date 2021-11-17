#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_controller.py
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.user.controller import blueprint
from app.user.service import role_permission_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/role/permission/rel/list')
@require_login
@require_permission
def query_role_permission_rel_list():
    """分页查询角色权限列表"""
    req = JsonParser(
        Argument('roleNo'),
        Argument('permissionNo'),
        Argument('roleName'),
        Argument('permissionName'),
        Argument('endpoint'),
        Argument('method'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_role_permission_rel_list(req)


@blueprint.get('/role/permission/unbound/list')
@require_login
@require_permission
def query_role_permission_unbound_list():
    """分页查询角色未绑定的权限列表"""
    req = JsonParser(
        Argument('roleNo'),
        Argument('permissionNo'),
        Argument('permissionName'),
        Argument('endpoint'),
        Argument('method'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_role_permission_unbound_list(req)


@blueprint.post('/role/permissions')
@require_login
@require_permission
def create_role_permissions():
    """批量新增角色权限"""
    req = JsonParser(
        Argument('roleNo'),
        Argument('permissionNumberList')
    ).parse()
    return service.create_role_permissions(req)


@blueprint.delete('/role/permission')
@require_login
@require_permission
def remove_role_permission():
    """删除角色权限"""
    req = JsonParser(
        Argument('roleNo'),
        Argument('permissionNo')
    ).parse()
    return service.remove_role_permission(req)


@blueprint.delete('/role/permissions')
@require_login
@require_permission
def remove_role_permissions():
    """批量删除角色权限"""
    req = JsonParser(
        Argument('roleNo'),
        Argument('permissionNumberList')
    ).parse()
    return service.remove_role_permissions(req)
