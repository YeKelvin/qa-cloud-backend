#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : global_helper
# @Time    : 2020/1/8 10:56
# @Author  : Kelvin.Ye
from flask import g

from server.librarys.decorators.classproperty import classproperty


class Global:
    @classproperty
    def logid(cls):
        return getattr(g, 'logid', None)

    @classproperty
    def user_no(cls):
        return getattr(g, 'user', None)

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
    def set(key, value):
        g.setdefault(key, value)
