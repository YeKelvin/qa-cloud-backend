#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2020/3/13 16:53
# @Author  : Kelvin.Ye
from flask import Blueprint


# TODO: 响应报文的Header添加名为 API-Version 的头，值为 day-month-year 格式的日期
# prefix: /rest/api/{v+版本号}/{module}/{resource}
# note  : /rest/api 由nginx代理，后端不需要处理
blueprint = Blueprint('script', __name__, url_prefix='/script')

from . import database_controller  # noqa
from . import element_controller  # noqa
from . import execution_controller  # noqa
from . import headers_controller  # noqa
from . import report_controller  # noqa
from . import testplan_controller  # noqa
from . import variables_controller  # noqa
