#!/usr/bin python3
# @Module  : openapi.scriptcenter.controller
# @File    : __init__.py
# @Time    : 2023-04-20 14:33:09
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('scriptcenter', __name__, url_prefix='/scriptcenter')


from . import execution_controller  # noqa
