#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_helper.py
# @Time    : 2020/1/8 10:56
# @Author  : Kelvin.Ye
from flask import g


# global_variables:
def get_logid():
    return getattr(g, 'logid', None)


def get_userno():
    return getattr(g, 'user_no', None)


def get_auth_token():
    return getattr(g, 'auth_token', None)


def get_auth_login_time():
    return getattr(g, 'auth_login_time', None)


def get_operator():
    return getattr(g, 'operator', None)


def get_success():
    return getattr(g, 'success', None)


def put(key, value):
    g.setdefault(key, value)
