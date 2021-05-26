#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_auth.py
# @Time    : 2019/11/12 16:29
# @Author  : Kelvin.Ye
import datetime

from server.utils.auth import JWTAuth


def test_auth_token():
    user_no = 'U00000001'
    token = JWTAuth.encode_auth_token(user_no, datetime.datetime.utcnow())
    print(token)
    payload = JWTAuth.decode_auth_token(token)
    print(payload)
