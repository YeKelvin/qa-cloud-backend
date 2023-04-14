#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2023-04-11 18:17:06
# @Author  : Kelvin.Ye
from flask import Blueprint


# note  : /rest/api 由nginx代理，后端不需要处理
blueprint = Blueprint('user', __name__, url_prefix='/usercenter')

from . import auth_controller  # noqa