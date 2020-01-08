#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from flask import Blueprint

from server.librarys.decorators import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.user import service
from server.utils.log_util import get_logger

log = get_logger(__name__)

blueprint = Blueprint('user', __name__, url_prefix='/user')


@blueprint.route('/login', methods=['POST'])
def login():
    """用户登录
    """
    req = JsonParser(
        Argument('username', required=True, nullable=False, help='账号或密码不能为空'),
        Argument('password', required=True, nullable=False, help='账号或密码不能为空'),
    ).parse()
    return service.login(req)


@blueprint.route('/logout', methods=['POST'])
@require_login
def logout():
    """用户登出
    """
    return service.logout()


@blueprint.route('/register', methods=['POST'])
@require_login
@require_permission
def register():
    """用户注册
    """
    req = JsonParser(
        Argument('username', required=True, nullable=False, help='用户名称不能为空'),
        Argument('nickname', required=True, nullable=False, help='用户昵称不能为空'),
        Argument('password', required=True, nullable=False, help='用户密码不能为空'),
        Argument('mobileNo'),
        Argument('email'),
    ).parse()
    return service.register(req)


@blueprint.route('/list', methods=['GET'])
@require_login
@require_permission
def user_list():
    """分页查询用户列表
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('username'),
        Argument('nickname'),
        Argument('mobileNo'),
        Argument('email'),
        Argument('state'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.user_list(req)


@blueprint.route('/info', methods=['GET'])
@require_login
def user_info():
    """查询个人用户信息
    """
    return service.user_info()


@blueprint.route('/info', methods=['PUT'])
@require_login
@require_permission
def modify_user():
    """更新用户信息
    """
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空'),
        Argument('username', required=True, nullable=False, help='用户名称不能为空'),
        Argument('nickname', required=True, nullable=False, help='用户昵称不能为空'),
        Argument('mobileNo'),
        Argument('email'),
    ).parse()
    return service.modify_user(req)


@blueprint.route('/info/state', methods=['PATCH'])
@require_login
@require_permission
def modify_user_state():
    """更新用户信息
    """
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空'),
        Argument('state', required=True, nullable=False, help='用户状态不能为空'),
    ).parse()
    return service.modify_user_state(req)


@blueprint.route('', methods=['DELETE'])
@require_login
@require_permission
def delete_user():
    """删除用户
    """
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空'),
    ).parse()
    return service.delete_user(req)


@blueprint.route('/role/permission/rel/list', methods=['GET'])
@require_login
@require_permission
def role_permission_rel_list():
    """分页查询权限列表
    """
    req = JsonParser(
        Argument('roleName'),
        Argument('permissionName'),
        Argument('endpoint'),
        Argument('method'),
        Argument('state'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.role_permission_rel_list(req)


@blueprint.route('/permission/list', methods=['GET'])
@require_login
@require_permission
def permission_list():
    req = JsonParser(
        Argument('permissionNo'),
        Argument('permissionName'),
        Argument('endpoint'),
        Argument('method'),
        Argument('state'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.permission_list(req)


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
        Argument('remark'),
    ).parse()
    return service.create_permission(req)


@blueprint.route('/permission', methods=['PUT'])
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


@blueprint.route('/permission', methods=['DELETE'])
def delete_permission():
    """删除权限
    """
    req = JsonParser(
        Argument('permissionNo', required=True, nullable=False, help='权限编号不能为空'),
    ).parse()
    return service.delete_permission(req)


@blueprint.route('/role/list', methods=['GET'])
@require_login
@require_permission
def role_list():
    """分页查询角色列表
    """
    req = JsonParser(
        Argument('roleName'),
    ).parse()
    return service.role_list(req)


@blueprint.route('/role', methods=['POST'])
@require_login
@require_permission
def create_role():
    """新增角色
    """
    req = JsonParser(
        Argument('roleName', required=True, nullable=False, help='角色名称不能为空'),
        Argument('remark', required=True, nullable=False, help='角色描述不能为空'),
    ).parse()
    return service.create_role(req)


@blueprint.route('/role', methods=['PUT'])
def modify_role():
    """更新角色信息
    """
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空'),
        Argument('roleName', required=True, nullable=False, help='角色名称不能为空'),
        Argument('remark'),
    ).parse()
    return service.modify_role(req)


@blueprint.route('/role', methods=['DELETE'])
def delete_role():
    """删除角色
    """
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空')
    ).parse()
    return service.delete_role(req)
