#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from flask import Blueprint


# TODO: prefix修改为 /rest/api/{v+版本号}/{module}/{resource}
# TODO: 响应报文的Header添加名为 API-Version 的头，值为 day-month-year 格式的日期
blueprint = Blueprint('user', __name__, url_prefix='/rest/api/user')

from . import auth_controller  # noqa
from . import permission_controller  # noqa
from . import role_controller  # noqa
from . import role_permission_controller  # noqa
from . import user_controller  # noqa
from . import user_role_controller  # noqa
