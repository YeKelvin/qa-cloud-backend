#!/usr/bin/ python3
# @File    : localvars.py
# @Time    : 2020/1/8 10:56
# @Author  : Kelvin.Ye
from flask import g


def get_trace_id():
    return getattr(g, 'trace_id', None)


def get_user_no():
    return getattr(g, 'user_no', None)


def get_userno_or_default():
    return getattr(g, 'user_no', '9999')


def get_issued_at():
    return getattr(g, 'issued_at', None)


def set(key, value):  # noqa
    g.setdefault(key, value)
