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


@blueprint.route('/register', methods=['POST'])
def register():
    """用户注册
    """
    req = JsonParser(
        Argument('username', required=True, nullable=False, help='用户名称不能为空'),
        Argument('nickname', required=True, nullable=False, help='昵称不能为空'),
        Argument('password', required=True, nullable=False, help='用户密码不能为空'),
        Argument('mobileNo'),
        Argument('email'),
    ).parse()
    return service.register(req)


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


@blueprint.route('/info', methods=['GET'])
@require_login
def info():
    """查询个人用户信息
    """
    return service.info()


@blueprint.route('/info/list', methods=['GET'])
@require_login
@require_permission
def info_list():
    """分页查询用户列表
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('userName'),
        Argument('nickName'),
        Argument('mobileNo'),
        Argument('email'),
        Argument('state'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.info_list(req)


@blueprint.route('/test/permission', methods=['POST'])
@require_login
@require_permission
def permission():
    return 'test require_permission'
