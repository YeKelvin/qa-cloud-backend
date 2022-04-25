#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_controller.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.usercenter.controller import blueprint
from app.usercenter.enum import PermissionState
from app.usercenter.service import permission_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/permission/list')
@require_login
@require_permission
def query_permission_list():
    """分页查询权限列表"""
    req = JsonParser(
        Argument('permissionNo'),
        Argument('permissionName'),
        Argument('permissionDesc'),
        Argument('endpoint'),
        Argument('method'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_permission_list(req)


@blueprint.get('/permission/all')
@require_login
@require_permission
def query_permission_all():
    """查询所有权限"""
    return service.query_permission_all()


@blueprint.post('/permission')
@require_login
@require_permission
def create_permission():
    """新增权限"""
    req = JsonParser(
        Argument('permissionName', required=True, nullable=False, help='权限名称不能为空'),
        Argument('permissionDesc'),
        Argument('endpoint', required=True, nullable=False, help='请求路由不能为空'),
        Argument('method', required=True, nullable=False, help='请求方法不能为空')
    ).parse()
    return service.create_permission(req)


@blueprint.put('/permission')
@require_login
@require_permission
def modify_permission():
    """更新权限信息"""
    req = JsonParser(
        Argument('permissionNo', required=True, nullable=False, help='权限编号不能为空'),
        Argument('permissionName', required=True, nullable=False, help='权限名称不能为空'),
        Argument('permissionDesc'),
        Argument('endpoint', required=True, nullable=False, help='请求路由不能为空'),
        Argument('method', required=True, nullable=False, help='请求方法不能为空')
    ).parse()
    return service.modify_permission(req)


@blueprint.patch('/permission/state')
@require_login
@require_permission
def modify_permission_state():
    """更新权限状态"""
    req = JsonParser(
        Argument('permissionNo', required=True, nullable=False, help='权限编号不能为空'),
        Argument('state', required=True, nullable=False, enum=PermissionState, help='权限状态不能为空')
    ).parse()
    return service.modify_permission_state(req)


@blueprint.delete('/permission')
@require_login
@require_permission
def remove_permission():
    """删除权限"""
    req = JsonParser(
        Argument('permissionNo', required=True, nullable=False, help='权限编号不能为空')
    ).parse()
    return service.remove_permission(req)
