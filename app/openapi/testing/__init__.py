#!/usr/bin python3
# @Module  : testing
# @File    : __init__.py
# @Time    : 2023-04-20 13:56:14
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('testing', __name__, url_prefix='/testing')


from .controller import testplan_controller  # noqa
