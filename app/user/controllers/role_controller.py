#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_route
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.user.controllers import blueprint
from app.user.services import role_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/role/list')
@require_login
@require_permission
def query_role_list():
    """分页查询角色列表
    """
    req = JsonParser(
        Argument('roleNo'),
        Argument('roleName'),
        Argument('roleDesc'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_role_list(req)


@blueprint.get('/role/all')
@require_login
@require_permission
def query_role_all():
    """查询所有角色
    """
    return service.query_role_all()


@blueprint.post('/role')
@require_login
@require_permission
def create_role():
    """新增角色
    """
    req = JsonParser(
        Argument('roleName', required=True, nullable=False, help='角色名称不能为空'),
        Argument('roleDesc', required=True, nullable=False, help='角色描述不能为空'),
    ).parse()
    return service.create_role(req)


@blueprint.put('/role')
@require_login
@require_permission
def modify_role():
    """更新角色信息
    """
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空'),
        Argument('roleName', required=True, nullable=False, help='角色名称不能为空'),
        Argument('roleDesc'),
    ).parse()
    return service.modify_role(req)


@blueprint.patch('/role/state')
@require_login
@require_permission
def modify_role_state():
    """更新角色状态
    """
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空'),
        Argument('state', required=True, nullable=False, help='角色状态不能为空'),
    ).parse()
    return service.modify_role_state(req)


@blueprint.delete('/role')
@require_login
@require_permission
def delete_role():
    """删除角色
    """
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空')
    ).parse()
    return service.delete_role(req)
