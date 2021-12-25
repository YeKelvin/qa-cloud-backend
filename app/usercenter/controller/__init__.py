#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from flask import Blueprint


# TODO: 响应报文的Header添加名为 API-Version 的头，值为 day-month-year 格式的日期
# prefix: /rest/api/{v+版本号}/{module}/{resource}
# note  : /rest/api 由nginx代理，后端不需要处理
blueprint = Blueprint('user', __name__, url_prefix='/usercenter')

from . import auth_controller  # noqa
from . import permission_controller  # noqa
from . import role_controller  # noqa
from . import role_permission_controller  # noqa
from . import user_controller  # noqa
from . import user_role_controller  # noqa
