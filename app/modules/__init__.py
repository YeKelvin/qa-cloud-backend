#!/usr/bin python3
# @Module  : modules
# @File    : __init__.py
# @Time    : 2023-04-19 11:57:49
# @Author  : Kelvin.Ye
from flask import Blueprint


restapi = Blueprint('restapi', __name__, url_prefix='/rest/api')

# noqa

# parent.register_blueprint(child)
