#!/usr/bin/ python3
# @File    : localvars.py
# @Time    : 2020/1/8 10:56
# @Author  : Kelvin.Ye
from contextvars import ContextVar

from flask import g

from app.tools.identity import new_ulid


traceid_var = ContextVar('trace_id')


def get_trace_id():
    traceid = getattr(g, 'trace_id', None) or traceid_var.get()
    if not traceid:
        traceid = new_ulid()
        traceid_var.set(traceid)
    return traceid


def get_user_no():
    return getattr(g, 'user_no', None)


def get_userno_or_default():
    return getattr(g, 'user_no', '9999')


def get_issued_at():
    return getattr(g, 'issued_at', None)


def setg(key, value):  # noqa
    g.setdefault(key, value)
