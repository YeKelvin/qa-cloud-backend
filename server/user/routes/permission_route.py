#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_route
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.user.services import permission_service as service
from server.user.routes import blueprint
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/permission/list', methods=['GET'])
@require_login
@require_permission
def query_permission_list():
    """分页查询权限列表
    """
    req = JsonParser(
        Argument('permissionNo'),
        Argument('permissionName'),
        Argument('endpoint'),
        Argument('method'),
        Argument('state'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_permission_list(req)


@blueprint.route('/permission/all', methods=['GET'])
@require_login
@require_permission
def query_permission_all():
    """查询所有权限
    """
    return service.query_permission_all()


@blueprint.route('/permission', methods=['POST'])
@require_login
@require_permission
def create_permission():
    """新增权限
    """
    req = JsonParser(
        Argument('permissionName', required=True, nullable=False, help='权限名称不能为空'),
        Argument('endpoint', required=True, nullable=False, help='请求路由不能为空'),
        Argument('method', required=True, nullable=False, help='请求方法不能为空'),
        Argument('description'),
    ).parse()
    return service.create_permission(req)


@blueprint.route('/permission', methods=['PUT'])
@require_login
@require_permission
def modify_permission():
    """更新权限信息
    """
    req = JsonParser(
        Argument('permissionNo', required=True, nullable=False, help='权限编号不能为空'),
        Argument('permissionName', required=True, nullable=False, help='权限名称不能为空'),
        Argument('endpoint', required=True, nullable=False, help='请求路由不能为空'),
        Argument('method', required=True, nullable=False, help='请求方法不能为空'),
    ).parse()
    return service.modify_permission(req)


@blueprint.route('/permission/state', methods=['PATCH'])
@require_login
@require_permission
def modify_permission_state():
    """更新权限状态
    """
    req = JsonParser(
        Argument('permissionNo', required=True, nullable=False, help='权限编号不能为空'),
        Argument('state', required=True, nullable=False, help='权限状态不能为空'),
    ).parse()
    return service.modify_permission_state(req)


@blueprint.route('/permission', methods=['DELETE'])
@require_login
@require_permission
def delete_permission():
    """删除权限
    """
    req = JsonParser(
        Argument('permissionNo', required=True, nullable=False, help='权限编号不能为空'),
    ).parse()
    return service.delete_permission(req)
