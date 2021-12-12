#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2021-08-18 15:04:36
# @Author  : Kelvin.Ye
from flask import Blueprint

# TODO: prefix修改为 /rest/api/{v+版本号}/{module}/{resource}
# TODO: 响应报文的Header添加名为 API-Version 的头，值为 day-month-year 格式的日期
blueprint = Blueprint('public', __name__, url_prefix='/rest/api/public')

from . import tag_controller  # noqa
from . import workspace_controller  # noqa
from . import workspace_user_controller  # noqa
