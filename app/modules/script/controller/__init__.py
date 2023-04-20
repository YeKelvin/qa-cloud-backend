#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2020/3/13 16:53
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('script', __name__, url_prefix='/script')


from . import database_controller   # noqa
from . import element_controller    # noqa
from . import execution_controller  # noqa
from . import httpheader_controller # noqa
from . import report_controller     # noqa
from . import testplan_controller   # noqa
from . import variables_controller  # noqa
