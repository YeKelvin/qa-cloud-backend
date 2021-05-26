#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_route
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login, require_permission
from app.common.parser import JsonParser, Argument
from app.user.controllers import blueprint
from app.user.services import user_service as service
from app.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/login', methods=['POST'])
def login():
    """用户登录
    """
    req = JsonParser(
        Argument('loginName', required=True, nullable=False, help='登录账号或密码不能为空'),
        Argument('password', required=True, nullable=False, help='登录账号或密码不能为空'),
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
        Argument('loginName', required=True, nullable=False, help='登录账号不能为空'),
        Argument('userName', required=True, nullable=False, help='用户名称不能为空'),
        Argument('password', required=True, nullable=False, help='用户密码不能为空'),
        Argument('mobileNo'),
        Argument('email'),
    ).parse()
    return service.register(req)


@blueprint.route('/password/reset', methods=['PATCH'])
@require_login
@require_permission
def reset_password():
    """重置密码
    """
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空'),
    ).parse()
    return service.reset_login_password(req)


@blueprint.route('/list', methods=['GET'])
@require_login
@require_permission
def query_user_list():
    """分页查询用户列表
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('userName'),
        Argument('mobileNo'),
        Argument('email'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_user_list(req)


@blueprint.route('/all', methods=['GET'])
@require_login
@require_permission
def query_user_all():
    """查询所有用户
    """
    return service.query_user_all()


@blueprint.route('/info', methods=['GET'])
@require_login
def query_user_info():
    """查询个人用户信息
    """
    return service.query_user_info()


@blueprint.route('/info', methods=['PUT'])
@require_login
@require_permission
def modify_user():
    """更新用户信息
    """
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空'),
        Argument('userName', required=True, nullable=False, help='用户名称不能为空'),
        Argument('mobileNo'),
        Argument('email'),
    ).parse()
    return service.modify_user(req)


@blueprint.route('/info/state', methods=['PATCH'])
@require_login
@require_permission
def modify_user_state():
    """更新用户状态
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
