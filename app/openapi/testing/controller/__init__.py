#!/usr/bin python3
# @Module  : openapi.testing.controller
# @File    : __init__.py
# @Time    : 2023-04-20 14:33:09
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('testing', __name__, url_prefix='/testing')


from . import testplan_controller  # noqa
