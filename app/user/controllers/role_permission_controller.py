#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_route
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.user.controllers import blueprint
from app.user.services import role_permission_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/role/permission/rel/list')
@require_login
@require_permission
def query_role_permission_rel_list():
    """分页查询角色权限关联关系列表
    """
    req = JsonParser(
        Argument('roleNo'),
        Argument('permissionNo'),
        Argument('roleName'),
        Argument('permissionName'),
        Argument('endpoint'),
        Argument('method'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_role_permission_rel_list(req)


@blueprint.post('/role/permission/rel')
@require_login
@require_permission
def create_role_permission_rel():
    """新增角色权限关联关系
    """
    req = JsonParser(
        Argument('roleNo'),
        Argument('permissionNo'),
    ).parse()
    return service.create_role_permission_rel(req)


@blueprint.delete('/role/permission/rel')
@require_login
@require_permission
def delete_role_permission_rel():
    """删除角色权限关联关系
    """
    req = JsonParser(
        Argument('roleNo'),
        Argument('permissionNo'),
    ).parse()
    return service.delete_role_permission_rel(req)
