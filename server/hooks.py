#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hooks.py
# @Time    : 2019/11/7 20:02
# @Author  : Kelvin.Ye
from flask import request, g

from server.user.auth import Auth
from server.user.model import TUser
from server.utils.log_util import get_logger

log = get_logger(__name__)


def before_request():
    if 'Authorization' in request.headers:
        auth_header = request.headers.get('Authorization')
        auth_token_arr = auth_header.split(' ')
        if not auth_token_arr or auth_token_arr[0] != 'JWT' or len(auth_token_arr) != 2:
            g.user = None
        else:
            auth_token = auth_token_arr[1]
            payload = Auth.decode_auth_token(auth_token)
            auth_token = auth_token_arr[1]
            try:
                payload = Auth.decode_auth_token(auth_token)
            except Exception:
                g.user = None
            g.user = TUser.query.filter_by(user_no=payload['data']['id']).first()
            g.payload = payload
    else:
        g.user = None


def after_request():
    log.info('after_request')


def error_handler():
    log.info('error_handler')
    return '404'
