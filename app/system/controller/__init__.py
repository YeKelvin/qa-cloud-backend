#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2021/6/2 00:08
# @Author  : Kelvin.Ye
from flask import Blueprint


# TODO: 响应报文的Header添加名为 API-Version 的头，值为 day-month-year 格式的日期
# prefix: /rest/api/{v+版本号}/{module}/{resource}
# note  : /rest/api 由nginx代理，后端不需要处理
blueprint = Blueprint('system', __name__, url_prefix='/system')

from . import log_controller  # noqa
