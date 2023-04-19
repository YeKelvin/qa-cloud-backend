#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2021/6/2 00:08
# @Author  : Kelvin.Ye
from flask import Blueprint


# note  : /rest/api 由nginx代理，后端不需要处理
blueprint = Blueprint('system', __name__, url_prefix='/system')

from . import log_controller  # noqa
