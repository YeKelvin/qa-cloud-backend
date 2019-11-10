#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from flask import Blueprint, request

from server.common.response import http_response
from server.user.auth import Auth
from server.user.model import TUser
from server.utils.log_util import get_logger

log = get_logger(__name__)

blueprint = Blueprint('user', __name__, url_prefix='/user')


@blueprint.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')


@blueprint.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return http_response('账号或密码不能为空')
    user = TUser.query.filter_by(username=username).first()
    log.debug(f'user={user}')
    if not user:
        return http_response('账号或密码不能为空')
    if user.check_password_hash(password):
        log.debug('密码校验通过')
        token = Auth.encode_auth_token(user.user_no)
        return http_response({'token': token})
    else:
        log.debug('密码校验失败')
        return http_response('账号或密码不能为空')


@blueprint.route('/logout', methods=['POST'])
def logout():
    pass


@blueprint.route('/info', methods=['get'])
def info():
    pass
