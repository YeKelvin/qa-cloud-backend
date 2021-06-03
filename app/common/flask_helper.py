#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_helper.py
# @Time    : 2020/1/8 10:56
# @Author  : Kelvin.Ye
from flask import g

from app.common.decorators.classproperty import classproperty


class GlobalVars:
    @classproperty
    def logid(cls):
        return getattr(g, 'logid', None)

    @classproperty
    def user_no(cls):
        return getattr(g, 'user_no', None)

    @classproperty
    def auth_token(cls):
        return getattr(g, 'auth_token', None)

    @classproperty
    def auth_login_time(cls):
        return getattr(g, 'auth_login_time', None)

    @classproperty
    def operator(cls):
        return getattr(g, 'operator', None)

    @classproperty
    def success(cls):
        return getattr(g, 'success', None)

    @staticmethod
    def put(key, value):
        g.setdefault(key, value)
