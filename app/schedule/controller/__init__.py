#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2022/5/13 14:47
# @Author  : Kelvin.Ye
from flask import Blueprint


# TODO: 响应报文的Header添加名为 API-Version 的头，值为 day-month-year 格式的日期
# prefix: /rest/api/{v+版本号}/{module}/{resource}
# note  : /rest/api 由nginx代理，后端不需要处理
blueprint = Blueprint('schedule', __name__, url_prefix='/schedule')

from . import task_controller  # noqa
