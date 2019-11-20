#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from flask import Blueprint, g

from server.librarys.decorators import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.user import service
from server.utils.log_util import get_logger

log = get_logger(__name__)

blueprint = Blueprint('user', __name__, url_prefix='/user')


@blueprint.route('/register', methods=['POST'])
def register():
    req = JsonParser(
        Argument('username', required=True, nullable=False, help='用户名称不能为空'),
        Argument('password', required=True, nullable=False, help='用户密码不能为空'),
        Argument('mobileNo'),
        Argument('email')
    ).parse()
    return service.register(req)


@blueprint.route('/login', methods=['POST'])
def login():
    req = JsonParser(
        Argument('username', required=True, nullable=False, help='账号或密码不能为空'),
        Argument('password', required=True, nullable=False, help='账号或密码不能为空')
    ).parse()
    return service.login(req)


@blueprint.route('/logout', methods=['POST'])
@require_login
def logout():
    return service.logout()


@blueprint.route('/info', methods=['POST'])
@require_login
def info():
    return service.info()


@blueprint.route('/menus', methods=['POST'])
def menus():
    return service.menus()


@blueprint.route('/test/token', methods=['POST'])
@require_login
def token():
    return 'test require_login'

# @blueprint.route('/test/permission', methods=['POST'])
# @require_permission
# def permission():
#     return 'test require_permission'
