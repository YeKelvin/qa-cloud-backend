#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_route
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.user.routes import blueprint
from server.user.services import role_service as service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/role/list', methods=['GET'])
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
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_role_list(req)


@blueprint.route('/role/all', methods=['GET'])
@require_login
@require_permission
def query_role_all():
    """查询所有角色
    """
    return service.query_role_all()


@blueprint.route('/role', methods=['POST'])
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


@blueprint.route('/role', methods=['PUT'])
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


@blueprint.route('/role/state', methods=['PATCH'])
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


@blueprint.route('/role', methods=['DELETE'])
@require_login
@require_permission
def delete_role():
    """删除角色
    """
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空')
    ).parse()
    return service.delete_role(req)


@blueprint.route('/role/rel/list', methods=['GET'])
@require_login
@require_permission
def query_user_role_rel_list():
    """分页查询用户角色关联关系列表
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
        Argument('userName'),
        Argument('roleName'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_user_role_rel_list(req)


@blueprint.route('/role/rel', methods=['POST'])
@require_login
@require_permission
def create_user_role_rel():
    """新增用户角色关联关系
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
    ).parse()
    return service.create_user_role_rel(req)


@blueprint.route('/role/rel', methods=['DELETE'])
@require_login
@require_permission
def delete_user_role_rel():
    """删除用户角色关联关系
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
    ).parse()
    return service.delete_user_role_rel(req)


@blueprint.route('/role/permission/rel/list', methods=['GET'])
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
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_role_permission_rel_list(req)


@blueprint.route('/role/permission/rel', methods=['POST'])
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


@blueprint.route('/role/permission/rel', methods=['DELETE'])
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
