#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from flask import Blueprint, request

from server.common.parser import JsonParser, Argument
from server.user import service
from server.utils.log_util import get_logger

log = get_logger(__name__)

blueprint = Blueprint('user', __name__, url_prefix='/user')


@blueprint.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')


@blueprint.route('/login', methods=['POST'])
def login():
    req, error = JsonParser(
        Argument('username', required=True, nullable=False, help='账号或密码不能为空'),
        Argument('password', required=True, nullable=False, help='账号或密码不能为空')
    ).parse()
    return service.login(req, error)


@blueprint.route('/logout', methods=['POST'])
def logout():
    pass


@blueprint.route('/info', methods=['POST'])
def info():
    pass


@blueprint.route('/menus', methods=['POST'])
def menus():
    pass
