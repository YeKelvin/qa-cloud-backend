#!/usr/bin python3
# @File    : flask_util.py
# @Time    : 2023-05-16 18:10:50
# @Author  : Kelvin.Ye
import flask


def get_flask_app():
    """获取当前 flask 实例"""
    return flask.current_app._get_current_object()  # noqa
