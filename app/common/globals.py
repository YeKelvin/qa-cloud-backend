#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : globals.py
# @Time    : 2020/1/8 10:56
# @Author  : Kelvin.Ye
from flask import g


def get_trace_id():
    return getattr(g, 'trace_id', None)


def get_userno():
    return getattr(g, 'user_no', None)


def get_issued_at():
    return getattr(g, 'issued_at', None)


def get_success():
    return getattr(g, 'success', None)


def put(key, value):
    g.setdefault(key, value)
