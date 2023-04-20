#!/usr/bin python3
# @Module  : openapi
# @File    : __init__.py
# @Time    : 2023-04-19 16:40:05
# @Author  : Kelvin.Ye
from flask import Blueprint


api = Blueprint('openapi', __name__, url_prefix='/open/api')


"""
uri: /open/api/xxx
header:
    app-no:     xxx
    app-secret: xxx
"""
