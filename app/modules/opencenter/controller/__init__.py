#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2023-04-17 17:14:19
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('opencenter', __name__, url_prefix='/opencenter')


from . import apilog_controller         # noqa
from . import application_controller    # noqa
