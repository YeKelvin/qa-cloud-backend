#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2021/6/2 00:08
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('system', __name__, url_prefix='/system')


from . import log_controller  # noqa
