#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2020/3/13 16:53
# @Author  : Kelvin.Ye
from flask import Blueprint


# TODO: prefix修改为 /rest/api/{v+版本号}/{module}/{resource}
# TODO: 响应报文的Header添加名为 API-Version 的头，值为 day-month-year 格式的日期
blueprint = Blueprint('script', __name__, url_prefix='/script')

from . import element_controller  # noqa
from . import element_package_controller  # noqa
from . import env_var_controller  # noqa
from . import execution_controller  # noqa
from . import http_header_controller  # noqa
from . import test_controller  # noqa
from . import workspace_controller  # noqa
