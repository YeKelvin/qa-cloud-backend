#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_auth.py
# @Time    : 2019/11/12 16:29
# @Author  : Kelvin.Ye
import datetime

from server.user.auth import Auth


def test_auth_token():
    user_no = 'U00000001'
    token = Auth.encode_auth_token(user_no, datetime.datetime.utcnow())
    print(token)
    payload = Auth.decode_auth_token(token)
    print(payload)
